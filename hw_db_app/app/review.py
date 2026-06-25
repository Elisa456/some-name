from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, CheckConstraint, Index
from sqlalchemy.sql import func
from app.database import Base
import enum


class ClientType(str, enum.Enum):
    PRIVATE = "private"
    COMMERCIAL = "commercial"


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String(100), nullable=False)
    author_type = Column(Enum(ClientType), default=ClientType.PRIVATE)
    rating = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="check_rating_range"),
        Index('ix_reviews_active_order', is_active, display_order),
    )