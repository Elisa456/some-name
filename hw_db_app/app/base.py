from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            **filters
    ) -> List[ModelType]:

        query = self.db.query(self.model)


        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)

        if order_by:
            if hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))

        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: CreateSchemaType) -> ModelType:

        obj_data = obj_in.dict(exclude_unset=True)
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:

        db_obj = self.get(id)
        if not db_obj:
            return None

        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        db_obj = self.get(id)
        if not db_obj:
            return False
        self.db.delete(db_obj)
        self.db.commit()
        return True

    def count(self, **filters) -> int:
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.count()

    def exists(self, **filters) -> bool:

        return self.count(**filters) > 0

    def bulk_create(self, objs_in: List[CreateSchemaType]) -> List[ModelType]:
        db_objs = []
        for obj_in in objs_in:
            obj_data = obj_in.dict(exclude_unset=True)
            db_obj = self.model(**obj_data)
            db_objs.append(db_obj)

        self.db.add_all(db_objs)
        self.db.commit()

        for db_obj in db_objs:
            self.db.refresh(db_obj)

        return db_objs

    def bulk_delete(self, ids: List[int]) -> int:

        deleted = self.db.query(self.model).filter(self.model.id.in_(ids)).delete(synchronize_session=False)
        self.db.commit()
        return deleted