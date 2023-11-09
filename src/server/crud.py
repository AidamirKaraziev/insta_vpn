from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_crud import CRUDBase
from server.models import Server
from ping3 import ping

from server.schemas import OutlineServerCreate, VlessServerCreate, ServerCreate, ServerUpdate


async def check_server_availability(address: str):
    if ping(address):
        return True
    return False


class CrudServer(CRUDBase[Server, ServerCreate, ServerUpdate]):
    obj_name = "Server"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}
    id_is_exist = {"num": 403, "message": f"А {obj_name} with that id already exists"}
    name_is_exist = {"num": 403, "message": f"А {obj_name} with that name already exists"}
    address_is_exist = {"num": 403, "message": f"А {obj_name} with that address already exists"}
    no_good_server = {"num": 403, "message": f"На серверах нет ни одного свободного места"}
    vpn_type_id_incorrectly_selected = {"num": 403, "message": f"Неправильно выбрано vpn_type_id"}
    api_url_is_exist = {"num": 403, "message": f"в api_url в {obj_name} уже есть в БД"}

    """ОБЩИЕ ФУНКЦИИ"""
    async def get_server_by_id(self, *, db: AsyncSession, id: int):
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def get_all_servers(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def delete_server(self, *, db: AsyncSession, id: int):
        """
        Удаляет сервер из БД и каскадно удаляются все связанные с ним ключи в таблицах:
        outline_key и vless_key.
        Vless_key продолжают работать, если не удалить marzban с сервера.
        """
        obj, code, indexes = await self.get_server_by_id(db=db, id=id)
        if code != 0:
            return None, code, None
        obj = await super().delete(db=db, id=id)
        return obj, 0, None

    # async def get_active_servers(self, *, db: AsyncSession):
    #     query = select(self.model).where(self.model.is_active == True)
    #     response = await db.execute(query)
    #     good_servers = response.scalars().all()
    #     return good_servers, 0, None
    #
    # async def delete_server(self, *, db: AsyncSession, id: int):
    #     obj, code, indexes = await self.get_server_by_id(db=db, id=id)
    #     if code != 0:
    #         return None, code, None
    #     obj = await super().delete(db=db, id=id)
    #     return obj, 0, None
    #
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

    # TODO возможно оставить универсальным
    async def update_server(self, *, db: AsyncSession, update_data: ServerUpdate, id: int):
        """
        2 проверить айди
        3 проверить имя
        4 проверить fact_client
        """
        # check_id
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
        objects = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
        return objects, 0, None

    """КОД ДЯЛ OUTLINE"""
    async def add_outline_server(self, *, db: AsyncSession, new_data: OutlineServerCreate):
        """Создает outline сервер в БД, проверяя
            id: int
            vpn_type_id: int
            name: str
            address: str
            port: str
            api_url: str
            cert_sha256: str
            max_client: int
            is_active: Optional[bool] = True"""
        """"""
        # check vpn type
        if new_data.vpn_type_id != 1:
            return None, self.vpn_type_id_incorrectly_selected, None
        server, code, indexes = await crud_server.get_server_by_id(db=db, id=new_data.id)
        if server is not None:
            return None, self.id_is_exist, None
        # check name
        query = select(self.model).where(self.model.name == new_data.name)
        response = await db.execute(query)
        if response.scalar_one_or_none() is not None:
            return None, self.name_is_exist, None
        if new_data.address is not None:
            query = select(self.model).where(self.model.address == new_data.address)
            response = await db.execute(query)
            if response.scalar_one_or_none() is not None:
                return None, self.address_is_exist, None
        query = select(self.model).where(self.model.api_url == new_data.api_url)
        response = await db.execute(query)
        if response.scalar_one_or_none() is not None:
            return None, self.api_url_is_exist, None

        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None


    """КОД ДЯЛ VLESS"""
    async def add_vless_server(self, *, db: AsyncSession, new_data: VlessServerCreate):
        pass


crud_server = CrudServer(Server)
