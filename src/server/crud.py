from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_crud import CRUDBase
from server.models import Server
from server.schemas import ServerCreate, ServerUpdate
from ping3 import ping


async def check_server_availability(address: str):
    if ping(address):
        return True
    return False


class CrudServer(CRUDBase[Server, ServerCreate, ServerUpdate]):
    obj_name = "Server"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}
    name_is_exist = {"num": 403, "message": f"А {obj_name} with that name already exists"}
    address_is_exist = {"num": 403, "message": f"А {obj_name} with that address already exists"}
    no_good_server = {"num": 403, "message": f"На серверах нет ни одного свободного места"}
    id_is_exist = {"num": 403, "message": f"А {obj_name} with that id already exists"}

    async def get_server_by_id(self, *, db: AsyncSession, id: int):
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def get_all_servers(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def get_active_servers(self, *, db: AsyncSession):
        query = select(self.model).where(self.model.is_active == True)
        response = await db.execute(query)
        good_servers = response.scalars().all()
        return good_servers, 0, None

    async def add_server(self, *, db: AsyncSession, new_data: ServerCreate):
        server, code, indexes = await self.get_server_by_id(db=db, id=new_data.id)
        if server is not None:
            return None, self.id_is_exist, None
        # check name
        query = select(self.model).where(self.model.name == new_data.name)
        response = await db.execute(query)
        if response.scalar_one_or_none() is not None:
            return None, self.name_is_exist, None
        if new_data.address is not None:
            query = select(self.model).where(self.model.address == new_data.address, self.model.id != new_data.id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is not None:
                return None, self.address_is_exist, None
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def update_server(self, *, db: AsyncSession, update_data: ServerUpdate, id: int):
        # check id
        this_obj, code, indexes = await self.get_server_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        if update_data.id is not None and update_data.id != this_obj.id:
            server, code, indexes = await self.get_server_by_id(db=db, id=update_data.id)
            if server is not None:
                return None, self.id_is_exist, None
        # check name
        if update_data.name is not None:
            query = select(self.model).where(self.model.name == update_data.name, self.model.id != id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is not None:
                return None, self.name_is_exist, None
        if update_data.address is not None:
            query = select(self.model).where(self.model.address == update_data.address, self.model.id != update_data.id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is not None:
                return None, self.address_is_exist, None
        objects = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
        return objects, 0, None

    async def delete_server(self, *, db: AsyncSession, id: int):
        obj, code, indexes = await self.get_server_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        obj = await super().delete(db=db, id=id)
        return obj, 0, None

    async def deactivate_server(self, *, db: AsyncSession, id: int):
        server, code, indexes = await self.get_server_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        update_data = ServerUpdate(is_active=False)
        server, code, indexes = await self.update_server(db=db, id=id, update_data=update_data)
        if code != 0:
            return None, code, None
        return server, 0, None

    async def activate_server(self, *, db: AsyncSession, id: int):
        server, code, indexes = await self.get_server_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        update_data = ServerUpdate(is_active=True)
        server, code, indexes = await self.update_server(db=db, id=id, update_data=update_data)
        if code != 0:
            return None, code, None
        return server, 0, None


crud_server = CrudServer(Server)
