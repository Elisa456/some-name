import datetime

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.review import Review
from app.schemas_review import ReviewCreate, ReviewUpdate


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def create_review(self, data: ReviewCreate) -> Review:
        review = Review(**data.dict())
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_reviews(
            self,
            page: int = 1,
            limit: int = 20
    ) -> Dict[str, Any]:
        query = self.db.query(Review).filter(Review.is_active == True)

        total = query.count()
        skip = (page - 1) * limit
        reviews = query.order_by(Review.display_order).offset(skip).limit(limit).all()

        return {
            "items": reviews,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }

    def update_review(self, id: int, data: ReviewUpdate) -> Optional[Review]:
        review = self.db.query(Review).filter(Review.id == id).first()
        if not review:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)

        review.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete_review(self, id: int) -> bool:
        review = self.db.query(Review).filter(Review.id == id).first()
        if not review:
            return False
        self.db.delete(review)
        self.db.commit()
        return True