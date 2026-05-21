from sqlalchemy.orm import Session
from models import UserProfile
from typing import Optional, List

def get_profiles(db: Session, age: Optional[int] = None) -> List[UserProfile]:
    query = db.query(UserProfile)
    if age is not None:
        query = query.filter(UserProfile.age == age)
    return query.all()

def get_profile_by_id(db: Session, profile_id: int) -> Optional[UserProfile]:
    return db.query(UserProfile).filter(UserProfile.id == profile_id).first()

def create_profile(db: Session, username: str, email: str, age: int) -> UserProfile:
    db_profile = UserProfile(username=username, email=email, age=age)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def update_profile(db: Session, profile_id: int, username: str, email: str, age: int) -> Optional[UserProfile]:
    db_profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if db_profile:
        db_profile.username = username
        db_profile.email = email
        db_profile.age = age
        db.commit()
        db.refresh(db_profile)
    return db_profile

def delete_profile(db: Session, profile_id: int) -> bool:
    db_profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if db_profile:
        db.delete(db_profile)
        db.commit()
        return True
    return False