from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Dict, Any, List
from app.application import Application, ApplicationStatus


class StatisticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_total_statistics(self) -> Dict[str, Any]:
        total = self.db.query(Application).count()

        status_stats = {}
        for status in ApplicationStatus:
            count = self.db.query(Application).filter(Application.status == status).count()
            status_stats[status.value] = count

        return {
            "total": total,
            "by_status": status_stats
        }

    def get_monthly_statistics(self) -> List[Dict[str, Any]]:
        results = self.db.query(
            extract('year', Application.created_at).label('year'),
            extract('month', Application.created_at).label('month'),
            func.count(Application.id).label('count')
        ).group_by('year', 'month').order_by('year', 'month').all()

        return [
            {"year": int(row[0]), "month": int(row[1]), "count": int(row[2])}
            for row in results
        ]