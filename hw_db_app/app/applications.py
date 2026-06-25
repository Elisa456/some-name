from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime
from typing import Optional
from app.application import ApplicationStatus, ServiceType


class ApplicationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., pattern=r'^\+7\d{10}$')
    email: Optional[EmailStr] = None
    description: Optional[str] = Field(None, max_length=2000)
    service_type: ServiceType = ServiceType.FULL

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str]
    description: Optional[str]
    service_type: ServiceType
    status: ApplicationStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int
    page: int
    pages: int