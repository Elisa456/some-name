from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.review import ClientType


class ReviewCreate(BaseModel):
    author: str = Field(..., min_length=1, max_length=100)
    author_type: Optional[ClientType] = ClientType.PRIVATE
    rating: int = Field(..., ge=1, le=5)
    content: str = Field(..., min_length=1, max_length=2000)
    display_order: Optional[int] = Field(0, ge=0)


class ReviewUpdate(BaseModel):
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    author_type: Optional[ClientType] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ReviewResponse(BaseModel):
    id: int
    author: str
    author_type: ClientType
    rating: int
    content: str
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int
    page: int
    pages: int