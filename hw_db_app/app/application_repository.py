from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from app.application import Application, ApplicationStatus, ServiceType
from app.base import BaseRepository
from app.applications import ApplicationCreate, ApplicationUpdate


class ApplicationRepository(BaseRepository[Application, ApplicationCreate, ApplicationUpdate]):
    def __init__(self, db: Session):
        super().__init__(Application, db)

    def get_with_filters(
            self,
            skip: int = 0,
            limit: int = 100,
            status: Optional[ApplicationStatus] = None,
            service_type: Optional[ServiceType] = None,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
            search: Optional[str] = None,
            order_by: Optional[str] = "created_at",
            order_desc: bool = True
    ) -> List[Application]:
        query = self.db.query(Application)

        if status:
            query = query.filter(Application.status == status)
        if service_type:
            query = query.filter(Application.service_type == service_type)
        if date_from:
            query = query.filter(func.date(Application.created_at) >= date_from)
        if date_to:
            query = query.filter(func.date(Application.created_at) <= date_to)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Application.name.ilike(search_term),
                    Application.phone.ilike(search_term),
                    Application.email.ilike(search_term),
                    Application.description.ilike(search_term)
                )
            )

        if order_by and hasattr(Application, order_by):
            order_column = getattr(Application, order_by)
            if order_desc:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())

        return query.offset(skip).limit(limit).all()

    def get_by_status(self, status: ApplicationStatus) -> List[Application]:

        return self.db.query(Application).filter(Application.status == status).all()

    def get_by_phone(self, phone: str, days: int = 30) -> List[Application]:

        date_from = datetime.utcnow() - timedelta(days=days)
        return self.db.query(Application).filter(
            Application.phone == phone,
            Application.created_at >= date_from
        ).order_by(Application.created_at.desc()).all()

    def get_by_email(self, email: str, days: int = 30) -> List[Application]:
        date_from = datetime.utcnow() - timedelta(days=days)
        return self.db.query(Application).filter(
            Application.email == email,
            Application.created_at >= date_from
        ).order_by(Application.created_at.desc()).all()

    def update_status(self, id: int, status: ApplicationStatus) -> Optional[Application]:

        application = self.get(id)
        if not application:
            return None

        application.status = status
        application.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(application)
        return application

    def bulk_update_status(self, ids: List[int], status: ApplicationStatus) -> int:

        result = self.db.query(Application).filter(
            Application.id.in_(ids)
        ).update(
            {
                Application.status: status,
                Application.updated_at: datetime.utcnow()
            },
            synchronize_session=False
        )
        self.db.commit()
        return result

    def get_statistics_by_status(self) -> Dict[str, int]:

        results = self.db.query(
            Application.status,
            func.count(Application.id).label('count')
        ).group_by(Application.status).all()

        stats = {status.value: 0 for status in ApplicationStatus}
        for status, count in results:
            if status:
                stats[status.value] = count

        return stats

    def get_monthly_statistics(self, months: int = 12) -> List[Dict[str, Any]]:

        results = self.db.query(
            func.extract('year', Application.created_at).label('year'),
            func.extract('month', Application.created_at).label('month'),
            func.count(Application.id).label('count')
        ).filter(
            Application.created_at >= datetime.utcnow() - timedelta(days=months * 30)
        ).group_by('year', 'month').order_by('year', 'month').all()

        return [
            {"year": int(year), "month": int(month), "count": int(count)}
            for year, month, count in results
        ]

    def get_daily_statistics(self, days: int = 30) -> List[Dict[str, Any]]:

        results = self.db.query(
            func.date(Application.created_at).label('date'),
            func.count(Application.id).label('count')
        ).filter(
            Application.created_at >= datetime.utcnow() - timedelta(days=days)
        ).group_by('date').order_by('date').all()

        return [
            {"date": str(date), "count": int(count)}
            for date, count in results
        ]

    def get_status_transitions(self, id: int) -> List[Dict[str, Any]]:

        application = self.get(id)
        if not application:
            return []

        return [
            {
                "status": application.status.value,
                "timestamp": application.created_at.isoformat(),
                "old_status": None
            }
        ]

    def get_applications_by_date_range(
            self,
            start_date: date,
            end_date: date
    ) -> List[Application]:
        return self.db.query(Application).filter(
            func.date(Application.created_at) >= start_date,
            func.date(Application.created_at) <= end_date
        ).order_by(Application.created_at.desc()).all()

    def count_by_service_type(self) -> Dict[str, int]:
        results = self.db.query(
            Application.service_type,
            func.count(Application.id).label('count')
        ).group_by(Application.service_type).all()

        stats = {service.value: 0 for service in ServiceType}
        for service_type, count in results:
            if service_type:
                stats[service_type.value] = count

        return stats