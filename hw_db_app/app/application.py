from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, CheckConstraint, Index
from sqlalchemy.sql import func
from app.database import Base
import enum


class ServiceType(str, enum.Enum):
    FULL = "full"
    MATERIALS = "materials"
    PROJECT = "project"
    CONSULT = "consult"


class ApplicationStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    service_type = Column(Enum(ServiceType), nullable=False, default=ServiceType.FULL)
    status = Column(Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.NEW)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("char_length(description) <= 2000", name="check_description_length"),
        Index('ix_applications_status_created', status, created_at),
    )