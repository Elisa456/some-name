from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.admin import AdminRole


class AdminCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: AdminRole = AdminRole.MANAGER


class AdminResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: AdminRole
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True