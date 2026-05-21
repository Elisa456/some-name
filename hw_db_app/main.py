from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field

from database import engine, get_db, Base
import models
import crud

# Создание таблиц в БД
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Profile API",
    description="API для управления профилями пользователей",
    version="1.0.0"
)


# Pydantic модели для валидации
class UserProfileCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    age: int = Field(..., ge=0, le=150)


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    age: int

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    age: int = Field(..., ge=0, le=150)


@app.get("/profiles", response_model=list[UserProfileResponse])
def get_profiles(
        age: Optional[int] = Query(None, ge=0, le=150, description="Фильтрация по возрасту"),
        db: Session = Depends(get_db)
):
    profiles = crud.get_profiles(db, age=age)
    return profiles


@app.post("/profiles", response_model=UserProfileResponse, status_code=201)
def create_profile(profile: UserProfileCreate, db: Session = Depends(get_db)):
    """
    Создать новый профиль пользователя
    """
    return crud.create_profile(
        db=db,
        username=profile.username,
        email=profile.email,
        age=profile.age
    )


@app.put("/profiles/{profile_id}", response_model=UserProfileResponse)
def update_profile(
        profile_id: int,
        profile: UserProfileUpdate,
        db: Session = Depends(get_db)
):
    """
    Полностью обновить профиль пользователя по ID
    """
    updated = crud.update_profile(
        db=db,
        profile_id=profile_id,
        username=profile.username,
        email=profile.email,
        age=profile.age
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return updated


@app.delete("/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_profile(db=db, profile_id=profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")
    return None


@app.get("/profiles/{profile_id}", response_model=UserProfileResponse)
def get_profile_by_id(profile_id: int, db: Session = Depends(get_db)):
    profile = crud.get_profile_by_id(db=db, profile_id=profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@app.get("/")
def root():
    return {
        "message": "Welcome to User Profile API",
        "endpoints": {
            "GET /profiles": "Get all profiles (filter by age)",
            "GET /profiles/{id}": "Get profile by ID",
            "POST /profiles": "Create new profile",
            "PUT /profiles/{id}": "Update profile",
            "DELETE /profiles/{id}": "Delete profile",
            "docs": "Swagger documentation"
        }
    }