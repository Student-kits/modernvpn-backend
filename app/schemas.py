from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_admin: bool
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class VPNConfigOut(BaseModel):
    id: int
    user_id: int
    server_id: str
    public_key: str
    ip_address: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None