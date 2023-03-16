from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel

from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import contains_eager

from db.db import Base
from models.general import ShortLink

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    # def update(self, *args, **kwargs):
    #     raise NotImplementedError
    #
    # def delete(self, *args, **kwargs):
    #     raise NotImplementedError


class RepositoryDB(Repository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.id == id)
        results = await db.execute(statement=statement)
        return results.unique().scalar_one_or_none()

    async def get_by_short_url(self, db: AsyncSession, short_url: str) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.short_url == short_url)
        results = await db.execute(statement=statement)
        return results.unique().scalar_one_or_none()

    async def get_multi(
            self,
            db: AsyncSession,
    ) -> List[ModelType]:
        statement = select(self._model).order_by('id')
        results = await db.execute(statement=statement)
        return results.scalars().unique().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # async def update(
    #         self,
    #         db: AsyncSession,
    #         *,
    #         db_obj: ModelType,
    #         obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    # ) -> ModelType:
    #     stmt = (
    #         update(Entity).
    #         where(Entity.id == db_obj.id).
    #         values(obj_in.dict(exclude_unset=True)).
    #         returning(Entity)
    #     )
    #     await db.execute(stmt)
    #     await db.commit()
    #
    #     return db_obj
    #
    # async def delete(
    #         self,
    #         db: AsyncSession,
    #         *,
    #         db_obj: ModelType,
    # ) -> ModelType:
    #     await db.delete(db_obj)
    #     await db.commit()
    #
    #     return db_obj
