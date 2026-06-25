from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from app.review import Review, ClientType
from app.base import BaseRepository
from app.schemas_review import ReviewCreate, ReviewUpdate


class ReviewRepository(BaseRepository[Review, ReviewCreate, ReviewUpdate]):
    def __init__(self, db: Session):
        super().__init__(Review, db)

    def get_active(
            self,
            skip: int = 0,
            limit: int = 100,
            order_by: str = "display_order"
    ) -> List[Review]:
        query = self.db.query(Review).filter(Review.is_active == True)

        if hasattr(Review, order_by):
            query = query.order_by(getattr(Review, order_by))

        return query.offset(skip).limit(limit).all()

    def get_by_rating(
            self,
            rating: int,
            skip: int = 0,
            limit: int = 100,
            active_only: bool = True
    ) -> List[Review]:
        query = self.db.query(Review).filter(Review.rating == rating)
        if active_only:
            query = query.filter(Review.is_active == True)

        return query.order_by(Review.display_order).offset(skip).limit(limit).all()

    def get_by_author_type(
            self,
            author_type: ClientType,
            skip: int = 0,
            limit: int = 100,
            active_only: bool = True
    ) -> List[Review]:
        query = self.db.query(Review).filter(Review.author_type == author_type)
        if active_only:
            query = query.filter(Review.is_active == True)

        return query.order_by(Review.display_order).offset(skip).limit(limit).all()

    def get_high_rated(self, min_rating: int = 4, limit: int = 10) -> List[Review]:

        return self.db.query(Review).filter(
            Review.rating >= min_rating,
            Review.is_active == True
        ).order_by(Review.rating.desc(), Review.display_order).limit(limit).all()

    def get_statistics(self) -> Dict[str, Any]:
        total = self.db.query(Review).filter(Review.is_active == True).count()

        avg_rating = self.db.query(
            func.avg(Review.rating)
        ).filter(Review.is_active == True).scalar()

        rating_distribution = self.db.query(
            Review.rating,
            func.count(Review.id).label('count')
        ).filter(Review.is_active == True).group_by(Review.rating).order_by(Review.rating).all()

        author_type_distribution = self.db.query(
            Review.author_type,
            func.count(Review.id).label('count')
        ).filter(Review.is_active == True).group_by(Review.author_type).all()

        return {
            "total": total,
            "average_rating": round(avg_rating or 0, 2),
            "rating_distribution": [
                {"rating": rating, "count": count}
                for rating, count in rating_distribution
            ],
            "author_type_distribution": [
                {"type": at.value if at else None, "count": count}
                for at, count in author_type_distribution
            ]
        }

    def get_max_display_order(self) -> int:
        result = self.db.query(func.max(Review.display_order)).scalar()
        return result or 0