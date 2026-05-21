from sqlalchemy import Column, Integer, String
from database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    age = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<UserProfile(id={self.id}, username='{self.username}', email='{self.email}', age={self.age})>"