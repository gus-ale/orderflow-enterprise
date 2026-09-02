import json, uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload
from .audit_client import audit_event
from .catalog_client import get_products
from .config import settings
from .database import Base, engine, get_db
from .event_workers import start_event_workers
from .inventory_client import ping_inventory, release_stock, reserve_stock
from .models import Order, OrderItem, OutboxEvent
from .schemas import OrderCreate, OrderRead
from .security import Principal, require_roles
from .observability import install_observability
from .tenant_client import order_month_limit
Base.metadata.create_all(bind=engine)

def now_iso(): return datetime.now(timezone.utc).isoformat()
@asynccontextmanager
async def lifespan(app:FastAPI):
    stop,threads=start_event_workers(); app.state.kafka_stop=stop
    try: yield
    finally:
        stop.set()
        for t in threads: t.join(timeout=8)
app=FastAPI(title='OrderFlow Order Service',version='1.1.0',description='Pedidos + gRPC Inventory + Transactional Outbox + Saga Kafka.',lifespan=lifespan)
install_observability(app)

def tenant_id_header(x_tenant_id:str|None=Header(None))->int:
    if not x_tenant_id or not x_tenant_id.isdigit() or int(x_tenant_id)<=0: raise HTTPException(400,"Falta X-Tenant-ID válido")
    return int(x_tenant_id)


@app.get('/api/orders',response_model=list[OrderRead])
def list_orders(limit:int=100,offset:int=0,db:Session=Depends(get_db),_:Principal=Depends(require_roles('ADMIN','MANAGER','SELLER')),tenant_id:int=Depends(tenant_id_header)):
    safe_limit=min(max(limit,1),500); safe_offset=max(offset,0)
    stmt=select(Order).where(Order.tenant_id==tenant_id).options(selectinload(Order.items)).order_by(Order.id.desc()).offset(safe_offset).limit(safe_limit)
    return db.scalars(stmt).all()
@app.post('/api/orders',response_model=OrderRead,status_code=201)
def create_order(payload:OrderCreate,request:Request,db:Session=Depends(get_db),p:Principal=Depends(require_roles('ADMIN','MANAGER','SELLER')),tenant_id:int=Depends(tenant_id_header)):
    limit=order_month_limit(tenant_id)
    month_start=datetime.now(timezone.utc).replace(day=1,hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
    month_count=db.scalar(select(func.count()).select_from(Order).where(Order.tenant_id==tenant_id,Order.created_at>=month_start)) or 0
    if month_count>=limit: raise HTTPException(409,f'Límite SaaS mensual de pedidos alcanzado: {limit}')
    operation_id=uuid.uuid4().hex; event_id=str(uuid.uuid4()); request_id=request.headers.get('x-request-id')
    quantities={}
    for item in payload.items: quantities[item.product_id]=quantities.get(item.product_id,0)+item.quantity
    normalized=[{'product_id':pid,'quantity':qty} for pid,qty in quantities.items()]
    catalog=get_products(list(quantities.keys()),tenant_id); reservation=reserve_stock(operation_id,normalized,request_id,tenant_id)
    try:
        order=Order(tenant_id=tenant_id,customer_name=payload.customer_name.strip(),status='PENDING_PAYMENT',total=0,reservation_id=operation_id); db.add(order); db.flush(); total=0.0; event_items=[]
        for reserved in reservation['items']:
            product=catalog[reserved['product_id']]; unit_price=float(product['price']); total += unit_price*reserved['quantity']
            db.add(OrderItem(order_id=order.id,product_id=reserved['product_id'],quantity=reserved['quantity'],unit_price=unit_price))
            event_items.append({'product_id':reserved['product_id'],'quantity':reserved['quantity'],'unit_price':unit_price})
        order.total=round(total,2)
        event={'event_id':event_id,'event_type':'orders.created','occurred_at':now_iso(),'tenant_id':tenant_id,'order_id':order.id,'reservation_id':operation_id,'customer_name':order.customer_name,'total':order.total,'items':event_items,'request_id':request_id}
        db.add(OutboxEvent(event_id=event_id,topic='orders.created',event_type='orders.created',aggregate_id=str(order.id),payload_json=json.dumps(event,ensure_ascii=False)))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        try: release_stock(operation_id,request_id,tenant_id)
        except HTTPException: pass
        raise HTTPException(status_code=500,detail='No se pudo persistir pedido + outbox; se intentó compensar inventario')
    saved=db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id==order.id))
    audit_event('order.create','order',p,f'id={saved.id}; total={saved.total}; reservation={operation_id}; status=PENDING_PAYMENT; outbox={event_id}',request)
    return saved
@app.get('/health')
def health():
    return {'status':'healthy','stage':17,'multi_tenant':True,'service':'order-service','database':'orderflow_orders','catalog_integration':'REST internal','inventory_integration':'gRPC + Protocol Buffers','inventory_grpc':ping_inventory(),'kafka':{'enabled':settings.kafka_enabled,'bootstrap':settings.kafka_bootstrap_servers,'outbox':'transactional','consumer_group':'order-saga-v1'}}
