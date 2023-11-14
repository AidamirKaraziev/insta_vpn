from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_crud import CRUDBase
from core.raise_template import raise_schemas

from outline.outline.outline_vpn.outline_vpn import OutlineVPN
from outline_key.models import OutlineKey
from outline_key.schemas import OutlineKeyUpdate, OutlineKeyCreate
from profiles.models import Profile
from server.crud import crud_server


class CrudOutlineKey(CRUDBase[OutlineKey, OutlineKeyCreate, OutlineKeyUpdate]):
    obj_name = "OutlineKey"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}
    not_found_by_server_id = {"num": 404, "message": f"Not found a {obj_name + 's'} with this server_id"}
    no_keys_available = {"num": 404, "message": f"No {obj_name + 's'} available"}

    async def get_all_keys(self, *, db: AsyncSession, skip: int, limit: int):
        """Получаем список Outline всех ключей"""

        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def get_key_by_id(self, *, db: AsyncSession, id: int):
        """Вывод ключа оп id, если такого нет - вывод ошибки с описанием"""
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    # TODO check how job check vpn_type_id
    async def get_keys_by_server_id(self, *, db: AsyncSession, server_id: int):
        """Вывод ключей по сервер id, если такого сервера нет - вывод ошибки с описанием."""
        server, code, indexes = await crud_server.get_server_by_id(db=db, id=server_id)
        if code != 0:
            return None, code, None
        if server.vpn_type_id != 1:
            return None, crud_server.vpn_type_id_incorrectly_selected, None
        query = select(self.model).where(self.model.server_id == server_id)
        response = await db.execute(query)
        obj = response.scalars().all()
        return obj, 0, None

    async def create_key(self, *, db: AsyncSession, server_id: int):
        """
        Подключается к Outline серверу. Если такого сервера нет - выдает ошибку с описанием.
        Создает Outline ключ. Записывает в БД.
        Если в процессе возникла исключение возвращает его.
        """
        server, code, indexes = await crud_server.get_server_by_id(db=db, id=server_id)
        if code != 0:
            return None, code, None
        try:
            client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
            key = client.create_key()
            new_data = OutlineKeyCreate(server_id=server_id, key_id=key.key_id, name=key.name, port=key.port,
                                        method=key.method, access_url=key.access_url, used_bytes=key.used_bytes,
                                        data_limit=key.data_limit, password=key.password, is_active=True)
            objects = await super().create(db_session=db, obj_in=new_data)
        except Exception as ex:
            return None, raise_schemas(ex), None
        return objects, 0, None

    async def creating_outline_keys_for_a_server(self, *, db: AsyncSession, server_id: int):
        """
        Создает Outline ключи для сервера, по server_id.
        Проверяет есть ли такой сервер, если нет - выдает ошибку с описанием.
        Проверяет, является ли этот сервер Outline по vpn_type_id, если нет - возвращает ошибку с описанием.
        Смотрит сколько ключей создано на сервере - создает недостающее количество.
        """
        server, code, indexes = await crud_server.get_server_by_id(db=db, id=server_id)
        if code != 0:
            return None, code, None
        if server.vpn_type_id != 1:
            return None, crud_server.vpn_type_id_incorrectly_selected, None

        client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
        much_to_create = server.max_client - int(len(client.get_keys()))
        for i in range(much_to_create):
            key, code, indexes = await self.create_key(db=db, server_id=server_id)
            if code != 0:
                return None, code, None
        keys, code, indexes = await self.get_key_by_id(db=db, id=server_id)
        return keys, 0, None

    async def deactivate_keys_by_server_id(self, db: AsyncSession, server_id: int):
        """Проверяет Деактивирует ключи """
        server, code, indexes = await crud_server.get_server_by_id(db=db, id=server_id)
        if code != 0:
            return None, code, None
        keys, code, indexes = await self.get_keys_by_server_id(db=db, server_id=server_id)
        for key in keys:
            update_data = OutlineKeyUpdate(is_active=False)
            await super().update(db_session=db, obj_current=key, obj_new=update_data)
        keys, code, indexes = await self.get_keys_by_server_id(db=db, server_id=server_id)
        if code != 0:
            return None, code, None
        return keys, 0, None

    async def activate_keys_by_server_id(self, db: AsyncSession, server_id: int):
        server, code, indexes = await crud_server.get_server_by_id(db=db, id=server_id)
        if code != 0:
            return None, code, None
        keys, code, indexes = await self.get_keys_by_server_id(db=db, server_id=server_id)
        for key in keys:
            update_data = OutlineKeyUpdate(is_active=True)
            await super().update(db_session=db, obj_current=key, obj_new=update_data)
        keys, code, indexes = await self.get_keys_by_server_id(db=db, server_id=server_id)
        if code != 0:
            return None, code, None
        return keys, 0, None

    async def get_quantity_free_keys(self, *, db: AsyncSession):
        """Выводит количество свободных ключей"""
        res = select(self.model).select_from(self.model).outerjoin(Profile).where(
            Profile.outline_key_id == None, self.model.is_active == True)
        response = await db.execute(res)
        quantity_free_keys = len(response.all())
        return quantity_free_keys, 0, None

    async def get_good_key(self, *, db: AsyncSession):
        """Возвращает один свободный ключ"""
        res = select(self.model).select_from(self.model).outerjoin(Profile).where(
            Profile.outline_key_id == None, self.model.is_active == True).limit(1)
        response = await db.execute(res)
        obj = response.scalar()
        if not obj:
            # TODO сделать отправку письма телеграм бота или какая-то другая логика. ВАЖНО!!!
            return None, self.no_keys_available, None
        return obj, 0, None


crud_outline_key = CrudOutlineKey(OutlineKey)

# # TODO change_max_client_to_server
# async def change_max_client_to_server(self, *, db: AsyncSession, server_id: int):
#     """Изменяет максимальное количество активных ключей на сервере"""
#     server, code, indexes = await crud_server.get_server_by_id(db=db, id=server_id)
#     if code != 0:
#         return None, code, None
#     if server.vpn_type_id != 1:
#         return None, crud_server.vpn_type_id_incorrectly_selected, None
#     max_client = server.max_client
#     # Проверяем количество профилей в бд
#     outline_keys, code, indexes = await self.get_keys_by_server_id(db=db, server_id=server_id)
#     if code != 0:
#         return None, code, None
#     fact_client = int(len(outline_keys))
#     if server.max_client > fact_client:
#         for key in range(server.max_client - fact_client):
#             new_key, code, indexes = await self.create_key(db=db, server_id=server_id)
#     elif server.max_client < fact_client:
#         # получить
#         pass
#     elif server.max_client == fact_client:
#         pass
#     # деактивирует все профили
#     # активирует outline ключи в количестве max_client
#
#     # create new keys
#     client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
#     keys_in_server = client.get_keys()
#     for key in range(server.max_client - len(keys_in_server)):
#         await self.create_key(db=db, server_id=server_id)
#     keys_in_server = client.get_keys()
#     # add in DB
#     for key in keys_in_server:
#         new_data = OutlineKeyCreate(server_id=server_id, key_id=key.key_id, name=key.name, port=key.port,
#                                     method=key.method, access_url=key.access_url, used_bytes=key.used_bytes,
#                                     data_limit=key.data_limit, password=key.password, is_active=True)
#     pass




    #
    # async def get_replacement_key(self, *, db: AsyncSession, Outline_key_id: int):
    #     Outline_key, code, indexes = await self.get_Outline_key_by_id(db=db, id=Outline_key_id)
    #     if code != 0:
    #         return None, code, None
    #
    #     res = select(self.model).select_from(self.model).outerjoin(Profile).where(
    #         Profile.Outline_key_id == None, self.model.is_active == True,
    #         self.model.server_id != Outline_key.server_id).limit(1)
    #     response = await db.execute(res)
    #     obj = response.scalar()
    #     if not obj:
    #         return None, self.no_keys_available, None
    #     return obj, 0, None
    #
