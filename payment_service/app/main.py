from contextlib import asynccontextmanager
from fastapi import Depends,FastAPI,Header,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import settings
from .database import Base,engine,get_db
from .models import Payment
from .security import Principal,require_roles
from .workers import start_workers
from .observability import install_observability
Base.metadata.create_all(bind=engine)
@asynccontextmanager
async def lifespan(app):
    stop,threads=start_workers()
    try: yield
    finally:
        stop.set(); [t.join(timeout=8) for t in threads]
app=FastAPI(title='OrderFlow Payment Service',version='1.0.0',description='Consumer Kafka + Outbox. Simula aprobación/rechazo para practicar Saga.',lifespan=lifespan)
install_observability(app)

def tenant_id_header(x_tenant_id:str|None=Header(None))->int:
    if not x_tenant_id or not x_tenant_id.isdigit() or int(x_tenant_id)<=0: raise HTTPException(400,'Falta X-Tenant-ID válido')
    return int(x_tenant_id)
@app.get('/api/payments')
def payments(db:Session=Depends(get_db),_:Principal=Depends(require_roles('ADMIN','MANAGER')),tenant_id:int=Depends(tenant_id_header)):
    rows=db.scalars(select(Payment).where(Payment.tenant_id==tenant_id).order_by(Payment.id.desc()).limit(200)).all(); return [{'id':r.id,'order_id':r.order_id,'amount':r.amount,'status':r.status,'reason':r.reason,'created_at':r.created_at} for r in rows]
@app.get('/health')
def health(): return {'status':'healthy','stage':17,'multi_tenant':True,'service':'payment-service','database':'orderflow_payments','kafka':settings.kafka_bootstrap_servers,'consumer_group':'payment-service-v1','reject_above_demo':settings.payment_reject_above}
