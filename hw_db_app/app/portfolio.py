from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, Index
from sqlalchemy.sql import func
from app.database import Base
import enum
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional
from app.portfolio import PortfolioCategory


class PortfolioCategory(str, enum.Enum):
    GARDEN = "garden"
    TERRACE = "terrace"
    COURTYARD = "courtyard"
    JAPANESE = "japanese"
    WINTER_GARDEN = "winter_garden"
    COMMERCIAL = "commercial"


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=False)
    image_alt = Column(String(200), nullable=True)
    category = Column(Enum(PortfolioCategory), nullable=True)
    year = Column(Integer, nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('ix_portfolio_active_order', is_active, display_order),
    )

class PortfolioCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    image_url: HttpUrl
    image_alt: Optional[str] = Field(None, max_length=200)
    category: Optional[PortfolioCategory] = None
    year: Optional[int] = Field(None, ge=2000, le=2030)
    display_order: Optional[int] = Field(0, ge=0)


class PortfolioUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    image_alt: Optional[str] = Field(None, max_length=200)
    category: Optional[PortfolioCategory] = None
    year: Optional[int] = Field(None, ge=2000, le=2030)
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class PortfolioResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    image_url: str
    image_alt: Optional[str]
    category: Optional[PortfolioCategory]
    year: Optional[int]
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class PortfolioListResponse(BaseModel):
    items: list[PortfolioResponse]
    total: int
    page: int
    pages: int