from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import date, datetime
from fastapi import HTTPException, status
from app.application import Application, ApplicationStatus, ServiceType
from app.applications import ApplicationCreate


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def create_application(self, data: ApplicationCreate) -> Application:
        application = Application(**data.dict())
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_application(self, id: int) -> Optional[Application]:
        return self.db.query(Application).filter(Application.id == id).first()

    def get_applications(
            self,
            page: int = 1,
            limit: int = 20,
            status: Optional[ApplicationStatus] = None,
            service_type: Optional[ServiceType] = None,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        query = self.db.query(Application)

        if status:
            query = query.filter(Application.status == status)
        if service_type:
            query = query.filter(Application.service_type == service_type)
        if date_from:
            query = query.filter(Application.created_at >= date_from)
        if date_to:
            query = query.filter(Application.created_at <= date_to)

        total = query.count()
        skip = (page - 1) * limit
        applications = query.order_by(Application.created_at.desc()).offset(skip).limit(limit).all()

        return {
            "items": applications,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }

    def update_status(self, id: int, status: ApplicationStatus) -> Optional[Application]:
        application = self.get_application(id)
        if not application:
            return None

        application.status = status
        application.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(application)
        return application