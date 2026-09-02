from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def utcnow(): return datetime.now(timezone.utc).replace(tzinfo=None)

class Tenant(Base):
    __tablename__ = 'tenants'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    plan: Mapped[str] = mapped_column(String(30), default='STARTER', index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    branches: Mapped[list['Branch']] = relationship(back_populates='tenant', cascade='all, delete-orphan')

class Branch(Base):
    __tablename__ = 'branches'
    __table_args__ = (UniqueConstraint('tenant_id','code',name='uq_branch_tenant_code'),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id', ondelete='CASCADE'), index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(160))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    tenant: Mapped[Tenant] = relationship(back_populates='branches')

class Membership(Base):
    __tablename__ = 'memberships'
    __table_args__ = (UniqueConstraint('tenant_id','user_id',name='uq_membership_tenant_user'),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id', ondelete='CASCADE'), index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    tenant_role: Mapped[str] = mapped_column(String(30), default='MEMBER', index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
