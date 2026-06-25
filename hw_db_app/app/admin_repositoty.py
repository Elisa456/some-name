from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.base import BaseRepository

class AdminRepository(BaseRepository[Admin, AdminCreate, AdminUpdate]):
    def __init__(self, db: Session):
        super().__init__(Admin, db)

    def get_by_email(self, email: str) -> Optional[Admin]:

        return self.db.query(Admin).filter(Admin.email == email).first()

    def get_by_email_or_id(self, identifier: str) -> Optional[Admin]:
        try:
            id_int = int(identifier)
            return self.get(id_int)
        except ValueError:
            return self.get_by_email(identifier)

    def update_last_login(self, id: int) -> Optional[Admin]:
        admin = self.get(id)
        if not admin:
            return None

        admin.last_login = datetime.utcnow()
        self.db.commit()
        self.db.refresh(admin)
        return admin

    def get_active_admins(self) -> List[Admin]:
        return self.db.query(Admin).filter(Admin.is_active == True).all()

    def get_admins_by_role(self, role: str) -> List[Admin]:
        return self.db.query(Admin).filter(Admin.role == role).all()

    def count_active(self) -> int:
        return self.db.query(Admin).filter(Admin.is_active == True).count()

    def update_password(self, id: int, new_password_hash: str) -> Optional[Admin]:

        admin = self.get(id)
        if not admin:
            return None

        admin.password_hash = new_password_hash
        self.db.commit()
        self.db.refresh(admin)
        return admin