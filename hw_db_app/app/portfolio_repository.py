from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional, Dict, Any
from app.portfolio import Portfolio, PortfolioCategory
from app.base import BaseRepository
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate


class PortfolioRepository(BaseRepository[Portfolio, PortfolioCreate, PortfolioUpdate]):
    def __init__(self, db: Session):
        super().__init__(Portfolio, db)

    def get_active(
            self,
            skip: int = 0,
            limit: int = 100,
            order_by: str = "display_order"
    ) -> List[Portfolio]:
        query = self.db.query(Portfolio).filter(Portfolio.is_active == True)

        if hasattr(Portfolio, order_by):
            query = query.order_by(getattr(Portfolio, order_by))

        return query.offset(skip).limit(limit).all()

    def get_by_category(
            self,
            category: PortfolioCategory,
            skip: int = 0,
            limit: int = 100,
            active_only: bool = True
    ) -> List[Portfolio]:
        query = self.db.query(Portfolio).filter(Portfolio.category == category)
        if active_only:
            query = query.filter(Portfolio.is_active == True)
        return query.order_by(Portfolio.display_order).offset(skip).limit(limit).all()

    def get_by_year(
            self,
            year: int,
            skip: int = 0,
            limit: int = 100,
            active_only: bool = True
    ) -> List[Portfolio]:
        query = self.db.query(Portfolio).filter(Portfolio.year == year)
        if active_only:
            query = query.filter(Portfolio.is_active == True)
        return query.order_by(Portfolio.display_order).offset(skip).limit(limit).all()

    def search(
            self,
            search_term: str,
            skip: int = 0,
            limit: int = 100,
            active_only: bool = True
    ) -> List[Portfolio]:
        search_pattern = f"%{search_term}%"
        query = self.db.query(Portfolio).filter(
            or_(
                Portfolio.title.ilike(search_pattern),
                Portfolio.description.ilike(search_pattern)
            )
        )
        if active_only:
            query = query.filter(Portfolio.is_active == True)

        return query.order_by(Portfolio.display_order).offset(skip).limit(limit).all()

    def get_categories_with_count(self, active_only: bool = True) -> List[Dict[str, Any]]:

        query = self.db.query(
            Portfolio.category,
            func.count(Portfolio.id).label('count')
        )
        if active_only:
            query = query.filter(Portfolio.is_active == True)

        results = query.group_by(Portfolio.category).all()

        return [
            {"category": cat.value if cat else None, "count": count}
            for cat, count in results
        ]

    def get_years_with_count(self, active_only: bool = True) -> List[Dict[str, Any]]:

        query = self.db.query(
            Portfolio.year,
            func.count(Portfolio.id).label('count')
        )
        if active_only:
            query = query.filter(Portfolio.is_active == True)

        results = query.filter(Portfolio.year.isnot(None)).group_by(Portfolio.year).order_by(
            Portfolio.year.desc()).all()

        return [
            {"year": year, "count": count}
            for year, count in results
        ]

    def reorder(self, items: List[Dict[str, Any]]) -> bool:

        try:
            for item in items:
                self.db.query(Portfolio).filter(
                    Portfolio.id == item['id']
                ).update({"display_order": item['display_order']})
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def get_max_display_order(self) -> int:
        result = self.db.query(func.max(Portfolio.display_order)).scalar()
        return result or 0

    def get_related_projects(
            self,
            project_id: int,
            category: Optional[PortfolioCategory] = None,
            limit: int = 4
    ) -> List[Portfolio]:
        project = self.get(project_id)
        if not project or not project.category:
            return []

        query = self.db.query(Portfolio).filter(
            Portfolio.id != project_id,
            Portfolio.category == project.category,
            Portfolio.is_active == True
        )

        return query.order_by(Portfolio.display_order).limit(limit).all()