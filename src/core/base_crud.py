from __future__ import annotations

import glob
import os
import shutil
import uuid

from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, UUID4
from fastapi import HTTPException, UploadFile
from fastapi_async_sqlalchemy import db
from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select, delete, update

from database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


# T = TypeVar("T", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    # def get_db(self) -> DBSessionMeta:
    #     return self.db
    def __init__(self, model: type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLModel model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.db = db

    async def get(
            self, *, id: int, db: AsyncSession | None = None
    ) -> ModelType | None:
        db_session = db or self.db.session
        query = select(self.model).where(self.model.id == id)
        response = await db_session.execute(query)
        return response.scalar_one_or_none()

    async def get_by_uuid(
            self, *, id: UUID4, db: AsyncSession | None = None
    ) -> ModelType | None:
        db_session = db or self.db.session
        query = select(self.model).where(self.model.id == id)
        response = await db_session.execute(query)
        return response.scalar_one_or_none()

    async def get_by_ids(
            self,
            *,
            list_ids: list[int],
            db_session: AsyncSession | None = None,
    ) -> list[ModelType] | None:
        db_session = db_session or self.db.session
        response = await db_session.execute(
            select(self.model).where(self.model.id.in_(list_ids))
        )
        return response.scalars().all()

    async def get_multi(
            self,
            *,
            skip: int = 0,
            limit: int = 100,
            db_session: AsyncSession | None = None,
    ) -> list[ModelType]:
        db_session = db_session or self.db.session
        query = select(self.model).offset(skip).limit(limit).order_by(self.model.id)
        response = await db_session.execute(query)
        return response.scalars().all()

    async def create(
            self,
            *,
            obj_in: CreateSchemaType | ModelType,
            db_session: AsyncSession | None = None,
    ) -> ModelType:
        db_session = db_session or self.db.session

        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore

        try:
            db_session.add(db_obj)
            await db_session.commit()
        except exc.IntegrityError:
            await db_session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Resource already exists",
            )
        await db_session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        *,
        obj_current: ModelType,
        obj_new: UpdateSchemaType | dict[str, Any] | ModelType,
        db_session: AsyncSession | None = None,
    ) -> ModelType:
        db_session = db_session or self.db.session
        obj_data = jsonable_encoder(obj_current)

        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.dict(
                exclude_unset=True
            )  # This tells Pydantic to not include the values that were not sent
        for field in obj_data:
            if field in update_data:
                setattr(obj_current, field, update_data[field])

        db_session.add(obj_current)
        await db_session.commit()
        await db_session.refresh(obj_current)
        return obj_current

    async def delete(self, *, id: int, db: AsyncSession | None = None):
        db_session = db or self.db.session
        obj = await self.get(db=db_session, id=id)  # Assuming you have a `get` method to retrieve the object by id
        if obj is not None:
            query = delete(self.model).where(self.model.id == id)
            await db_session.execute(query)
            await db_session.commit()
        return obj

    async def adding_file(self, db: AsyncSession, *, file: Optional[UploadFile],
                          base_path: str, path_model: str, path_type: str, db_obj: ModelType):
        all_path = base_path + path_model + "/" + str(db_obj.id) + "/" + path_type + "/"
        if path_type not in db_obj.__dict__.keys():
            return HTTPException(status_code=400,
                                 detail=f"Не понял что за ошибка но если она выпадет то будет понятно ")
        if file is None:
            # Удаляем все содержимое папки
            path_to_clear = all_path + "*"
            for file_to_clear in glob.glob(path_to_clear):
                os.remove(file_to_clear)
            #  обновить в базе данных ячейку
            query = update(self.model).where(self.model.id == db_obj.id).values({path_type: None}).returning(self.model)
            await db.execute(query)
            await db.commit()
            return {path_type: None}

        filename = uuid.uuid4().hex + os.path.splitext(file.filename)[1]
        element = [path_model, str(db_obj.id), path_type, filename]
        path_for_db = "/".join(element)

        if not os.path.exists(all_path):
            os.makedirs(all_path)
        # Удаляем все содержимое папки
        path_to_clear = all_path + "*"
        for file_to_clear in glob.glob(path_to_clear):
            os.remove(file_to_clear)
        with open(all_path + filename, "wb") as wf:
            shutil.copyfileobj(file.file, wf)
            file.file.close()  # удаляет временный
        query = update(self.model).where(self.model.id == db_obj.id).values({path_type: path_for_db}).returning(
            self.model)
        await db.execute(query)
        await db.commit()

        if not file:
            return HTTPException(status_code=400,
                                 detail=f"Не понял что за ошибка но если она выпадет то будет понятно ")
        else:
            return {path_type: path_for_db}

    def outline_error(self, ex: Exception):
        return {"num": 403, "message": f"Error in outline Server {ex}"}

    # async def get_count(
    #     self, db_session: AsyncSession | None = None
    # ) -> ModelType | None:
    #     db_session = db_session or self.db.session
    #     response = await db_session.execute(
    #         select(func.count()).select_from(select(self.model).subquery())
    #     )
    #     return response.scalar_one()
    #

    # async def get_multi_paginated(
    #     self,
    #     *,
    #     params: Params | None = Params(),
    #     query: T | Select[T] | None = None,
    #     db_session: AsyncSession | None = None,
    # ) -> Page[ModelType]:
    #     db_session = db_session or self.db.session
    #     if query is None:
    #         query = select(self.model)
    #     return await paginate(db_session, query, params)
    #
    # async def get_multi_paginated_ordered(
    #     self,
    #     *,
    #     params: Params | None = Params(),
    #     order_by: str | None = None,
    #     order: IOrderEnum | None = IOrderEnum.ascendent,
    #     query: T | Select[T] | None = None,
    #     db_session: AsyncSession | None = None,
    # ) -> Page[ModelType]:
    #     db_session = db_session or self.db.session
    #
    #     columns = self.model.__table__.columns
    #
    #     if order_by is None or order_by not in columns:
    #         order_by = "id"
    #
    #     if query is None:
    #         if order == IOrderEnum.ascendent:
    #             query = select(self.model).order_by(columns[order_by].asc())
    #         else:
    #             query = select(self.model).order_by(columns[order_by].desc())
    #
    #     return await paginate(db_session, query, params)
    #
    # async def get_multi_ordered(
    #     self,
    #     *,
    #     skip: int = 0,
    #     limit: int = 100,
    #     order_by: str | None = None,
    #     order: IOrderEnum | None = IOrderEnum.ascendent,
    #     db_session: AsyncSession | None = None,
    # ) -> list[ModelType]:
    #     db_session = db_session or self.db.session
    #
    #     columns = self.model.__table__.columns
    #
    #     if order_by is None or order_by not in columns:
    #         order_by = "id"
    #
    #     if order == IOrderEnum.ascendent:
    #         query = (
    #             select(self.model)
    #             .offset(skip)
    #             .limit(limit)
    #             .order_by(columns[order_by].asc())
    #         )
    #     else:
    #         query = (
    #             select(self.model)
    #             .offset(skip)
    #             .limit(limit)
    #             .order_by(columns[order_by].desc())
    #         )
    #
    #     response = await db_session.execute(query)
    #     return response.scalars().all()
    #


    # async def remove(
    #     self, *, id: UUID | str, db_session: AsyncSession | None = None
    # ) -> ModelType:
    #     db_session = db_session or self.db.session
    #     response = await db_session.execute(
    #         select(self.model).where(self.model.id == id)
    #     )
    #     obj = response.scalar_one()
    #     await db_session.delete(obj)
    #     await db_session.commit()
    #     return obj
