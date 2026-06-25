from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status
from datetime import datetime
from app.admin import Admin
from app.admin import AdminCreate, AdminLogin


class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def create_admin(self, data: AdminCreate) -> Admin:
        if self.db.query(Admin).filter(Admin.email == data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin with this email already exists"
            )

        admin = Admin(
            email=data.email,
            password_hash=get_password_hash(data.password),
            full_name=data.full_name,
            role=data.role
        )
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        return admin

    def get_admin(self, id: int) -> Optional[Admin]:
        return self.db.query(Admin).filter(Admin.id == id).first()

    def get_by_email(self, email: str) -> Optional[Admin]:
        return self.db.query(Admin).filter(Admin.email == email).first()

    def login(self, data: AdminLogin) -> dict:
        admin = self.get_by_email(data.email)
        if not admin or not verify_password(data.password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )

        admin.last_login = datetime.utcnow()
        self.db.commit()

        return {
            "access_token": create_access_token({"sub": str(admin.id)}),
            "refresh_token": create_refresh_token({"sub": str(admin.id)}),
            "token_type": "bearer"
        }

    def refresh_token(self, refresh_token: str) -> dict:
        payload = verify_token(refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        admin_id = payload.get("sub")
        admin = self.get_admin(int(admin_id))
        if not admin or not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin not found or inactive"
            )

        return {
            "access_token": create_access_token({"sub": str(admin.id)}),
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }