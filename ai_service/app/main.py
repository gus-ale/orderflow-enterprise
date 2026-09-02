from pathlib import Path
from fastapi import Depends,FastAPI,Request
from prometheus_client import Counter
from .agent import ReadOnlyBusinessAgent
from .config import settings
from .data_client import LiveDataClient
from .intelligence import demand_forecast,replenishment_plan,detect_order_anomalies
from .observability import RAG_QUERIES,TOOL_CALLS,install_observability
from .retrieval import KnowledgeIndex
from .schemas import AgentQuery,RagQuery
from .security import Principal,require_roles,tenant_id_header

app=FastAPI(title='OrderFlow AI Service',version='1.0.0',description='Stage 18: IA empresarial tenant-aware, RAG, forecasting, anomalías y agente read-only.')
install_observability(app)
KNOWLEDGE=KnowledgeIndex(Path(__file__).resolve().parents[1]/settings.knowledge_dir)
BI_ROLE=Depends(require_roles('ADMIN','MANAGER'))

def data_client(request:Request,tenant_id:int): return LiveDataClient(request,tenant_id)

@app.get('/api/ai/forecast')
def forecast(request:Request,days:int=14,_:Principal=BI_ROLE,tenant_id:int=Depends(tenant_id_header)):
    data=data_client(request,tenant_id); TOOL_CALLS.labels('forecast').inc()
    return {'tenant_id':tenant_id,'horizon_days':days,'items':demand_forecast(data.orders(),data.products(),max(1,min(days,90))),'method':'interpretable weighted recent-demand + trend','model_external':False}

@app.get('/api/ai/replenishment')
def replenishment(request:Request,days:int=14,_:Principal=BI_ROLE,tenant_id:int=Depends(tenant_id_header)):
    data=data_client(request,tenant_id); TOOL_CALLS.labels('replenishment').inc(); horizon=max(1,min(days,90))
    fc=demand_forecast(data.orders(),data.products(),horizon)
    return {'tenant_id':tenant_id,'horizon_days':horizon,'items':replenishment_plan(fc,data.inventory(),horizon),'advisory_only':True}

@app.get('/api/ai/anomalies')
def anomalies(request:Request,_:Principal=BI_ROLE,tenant_id:int=Depends(tenant_id_header)):
    data=data_client(request,tenant_id); TOOL_CALLS.labels('anomaly_detection').inc(); rows=detect_order_anomalies(data.orders())
    return {'tenant_id':tenant_id,'count':len(rows),'items':rows,'method':'robust median/MAD','advisory_only':True}

@app.post('/api/ai/rag')
def rag(payload:RagQuery,_:Principal=BI_ROLE,tenant_id:int=Depends(tenant_id_header)):
    RAG_QUERIES.inc(); result=KNOWLEDGE.answer(payload.question,payload.top_k)
    return {'tenant_id':tenant_id,**result,'scope':'OrderFlow curated technical knowledge','external_llm_used':False}

@app.post('/api/ai/ask')
def ask(payload:AgentQuery,request:Request,_:Principal=BI_ROLE,tenant_id:int=Depends(tenant_id_header)):
    data=data_client(request,tenant_id); agent=ReadOnlyBusinessAgent(data,KNOWLEDGE,settings.max_agent_steps); result=agent.run(payload.question,payload.horizon_days)
    for tool in result['tools']: TOOL_CALLS.labels(tool).inc()
    return {'tenant_id':tenant_id,'question':payload.question,**result,'policy':'READ_ONLY_BY_DEFAULT'}

@app.get('/api/ai/capabilities')
def capabilities(_:Principal=BI_ROLE,tenant_id:int=Depends(tenant_id_header)):
    return {'tenant_id':tenant_id,'capabilities':['demand_forecast','stock_replenishment','order_anomaly_detection','rag','natural_language_business_agent'],'guardrails':['tenant isolation','JWT/RBAC','read-only tools','human approval for writes','grounded RAG sources','no external model required']}

@app.get('/health')
def health(): return {'status':'healthy','stage':18,'service':'ai-service','tenant_aware':True,'knowledge_chunks':len(KNOWLEDGE.chunks),'external_llm_required':False,'agent_mode':'read-only'}
