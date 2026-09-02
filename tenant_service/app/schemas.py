from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
PlanName = Literal['STARTER','PRO','ENTERPRISE']
TenantRole = Literal['OWNER','TENANT_ADMIN','MANAGER','MEMBER']
class TenantCreate(BaseModel):
    slug: str = Field(min_length=2,max_length=80,pattern=r'^[a-z0-9-]+$')
    name: str = Field(min_length=2,max_length=160)
    plan: PlanName = 'STARTER'
class TenantRead(BaseModel):
    id:int; slug:str; name:str; plan:str; is_active:bool; created_at:datetime
    tenant_role:str|None=None
    model_config=ConfigDict(from_attributes=True)
class BranchCreate(BaseModel):
    code:str=Field(min_length=1,max_length=40,pattern=r'^[A-Za-z0-9_-]+$')
    name:str=Field(min_length=2,max_length=160)
class BranchRead(BaseModel):
    id:int; tenant_id:int; code:str; name:str; is_active:bool; created_at:datetime
    model_config=ConfigDict(from_attributes=True)
class MembershipCreate(BaseModel):
    user_id:int=Field(gt=0)
    tenant_role:TenantRole='MEMBER'
class MembershipRead(BaseModel):
    id:int; tenant_id:int; user_id:int; tenant_role:str; is_active:bool; created_at:datetime
    model_config=ConfigDict(from_attributes=True)
class PlanUpdate(BaseModel): plan:PlanName

class TenantStatusUpdate(BaseModel):
    is_active: bool
