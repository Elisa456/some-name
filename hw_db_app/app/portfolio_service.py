from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.portfolio import Portfolio, PortfolioCategory
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate


class PortfolioService:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, data: PortfolioCreate) -> Portfolio:
        project = Portfolio(**data.dict())
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project(self, id: int) -> Optional[Portfolio]:
        return self.db.query(Portfolio).filter(Portfolio.id == id).first()

    def get_projects(
            self,
            page: int = 1,
            limit: int = 20,
            category: Optional[PortfolioCategory] = None,
            year: Optional[int] = None
    ) -> Dict[str, Any]:
        query = self.db.query(Portfolio).filter(Portfolio.is_active == True)

        if category:
            query = query.filter(Portfolio.category == category)
        if year:
            query = query.filter(Portfolio.year == year)

        total = query.count()
        skip = (page - 1) * limit
        projects = query.order_by(Portfolio.display_order).offset(skip).limit(limit).all()

        return {
            "items": projects,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }

    def update_project(self, id: int, data: PortfolioUpdate) -> Optional[Portfolio]:
        project = self.get_project(id)
        if not project:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        project.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, id: int) -> bool:
        project = self.get_project(id)
        if not project:
            return False
        self.db.delete(project)
        self.db.commit()
        return True