from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VPNConfig(Base):
    __tablename__ = 'vpn_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    server_id = Column(String)
    private_key = Column(String)
    public_key = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdEvent(Base):
    __tablename__ = 'ad_events'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    event_type = Column(String)  # 'view', 'click', 'conversion'
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())