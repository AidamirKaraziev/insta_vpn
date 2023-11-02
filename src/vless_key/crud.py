from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_crud import CRUDBase
from vless_key.models import VlessKey
from vless_key.shcemas import VlessKeyUpdate, VlessKeyCreate


class CrudVlessKey(CRUDBase[VlessKey, VlessKeyCreate, VlessKeyUpdate]):
    obj_name = "VlessKey"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}
    no_keys_available = {"num": 404, "message": f"No {obj_name + 's'} available"}
    link_already = {"num": 403, "message": f"{obj_name} link already exist"}
    not_found_server_ip = {"num": 403, "message": f"Not found server ip"}

    async def get_all_vless_keys(self, *, db: AsyncSession, skip: int, limit: int):
        """Возвращает все Vless key из БД"""
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def get_vless_key_by_id(self, *, db: AsyncSession, id: int):
        """Возвращает Vless key из БД по id, если такого нет выводит ошибку с описанием"""
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def get_by_link(self, *, db: AsyncSession, link: str):
        """Возвращает Vless key из БД по link"""
        query = select(self.model).where(self.model.link == link)
        response = await db.execute(query)
        obj = response.scalar_one_or_none()
        return obj, 0, None

    async def check_server_ip(self, *, db: AsyncSession, server_ip: str):
        """Проверят есть ли БД такой server_ip, если нет выводит ошибку с описанием"""
        query = select(self.model).where(self.model.server_ip == server_ip).limit(1)
        response = await db.execute(query)
        obj = response.scalar_one_or_none()
        if obj is None:
            return None, self.not_found_server_ip, None
        return obj, 0, None

    async def create_key(self, *, db: AsyncSession, new_data: VlessKeyCreate):
        """Создает VLESS ключ в базе данных, проверяя есть ли такой link в БД"""
        vless_key, code, indexes = await self.get_by_link(db=db, link=new_data.link)
        if vless_key is not None:
            return None, self.link_already, None
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def create_many_keys_with_server_ip(self, *, db: AsyncSession, list_link: list, server_ip: str):
        """Создает список VLESS ключи в БД, проверяя есть ли такой link в БД"""
        new_link = []
        bad_link = []
        for link in list_link:
            new_data = VlessKeyCreate(server_ip=server_ip, link=link)
            vless_key, code, indexes = await self.create_key(db=db, new_data=new_data)
            if code != 0:
                bad_link.append(link)
            if code == 0:
                new_link.append(link)
        keys, code, indexes = await self.get_vless_keys_by_server_ip(db=db, server_ip=server_ip)
        response = {
            "Ключей к созданию": f"{len(list_link)}",
            "Создано ключей": f"{len(new_link)}",
            "Не создано": f"{len(bad_link)}",
            "Ключей с этим server_ip": f"{len(keys)}"
        }
        return response, 0, None

    async def get_vless_keys_by_server_ip(self, *, db: AsyncSession, server_ip: str):
        """Получить ключи по server_ip.
           Проверяет, есть ли такой server_ip, если нет -> возвращает ошибку с описанием.
        """
        first_obj, code, indexes = await self.check_server_ip(db=db, server_ip=server_ip)
        if code != 0:
            return None, code, None
        query = select(self.model).where(self.model.server_ip == server_ip)
        response = await db.execute(query)
        obj = response.scalars().all()
        return obj, 0, None

    async def deactivate_keys_by_server_ip(self, db: AsyncSession, server_ip: str):
        """
        Деактивирует VLESS ключи по server_ip.
        Проверяет, есть ли такой server_ip, если нет -> возвращает ошибку с описанием.
        """
        first_obj, code, indexes = await self.check_server_ip(db=db, server_ip=server_ip)
        if code != 0:
            return None, code, None
        keys, code, indexes = await self.get_vless_keys_by_server_ip(db=db, server_ip=server_ip)
        for key in keys:
            update_data = VlessKeyUpdate(is_active=False)
            await super().update(db_session=db, obj_current=key, obj_new=update_data)
        keys, code, indexes = await self.get_vless_keys_by_server_ip(db=db, server_ip=server_ip)
        return keys, 0, None

    async def activate_keys_by_server_ip(self, db: AsyncSession, server_ip: str):
        """
        Деактивирует VLESS ключи по server_ip.
        Проверяет, есть ли такой server_ip, если нет -> возвращает ошибку с описанием.
        """
        first_obj, code, indexes = await self.check_server_ip(db=db, server_ip=server_ip)
        if code != 0:
            return None, code, None
        keys, code, indexes = await self.get_vless_keys_by_server_ip(db=db, server_ip=server_ip)
        for key in keys:
            update_data = VlessKeyUpdate(is_active=True)
            await super().update(db_session=db, obj_current=key, obj_new=update_data)
        keys, code, indexes = await self.get_vless_keys_by_server_ip(db=db, server_ip=server_ip)
        return keys, 0, None

    async def delete_keys_by_server_ip(self, *, db: AsyncSession, server_ip: str):
        keys, code, indexes = await self.get_vless_keys_by_server_ip(db=db, server_ip=server_ip)
        if code != 0:
            return None, code, None
        for key in keys:
            await super().delete(db=db, id=key.id)
        response = f"Ключи с server_ip: {server_ip} удалены!"
        return response, 0, None

    """Возможно нужные апи, но пока что ХЗ зачем"""
    # TODO delete by id
    # TODO deactivate by id
    # TODO activate by id


crud_vless_key = CrudVlessKey(VlessKey)


# # TODO протестировать
# async def get_free_key(self, *, db: AsyncSession):
#     res = select(self.model).select_from(self.model).outerjoin(Profile).where(
#         Profile.vless_key_id == None, self.model.is_active == True).limit(1)
#     response = await db.execute(res)
#     obj = response.scalar()
#     if not obj:
#         # TODO сделать отправку письма телеграм бота или какая-то другая логика. ВАЖНО!!!
#         return None, self.no_keys_available, None
#     return obj, 0, None
#
# async def get_replacement_key(self, *, db: AsyncSession, vless_key_id: int):
#     vless_key, code, indexes = await self.get_vless_key_by_id(db=db, id=vless_key_id)
#     if code != 0:
#         return None, code, None
#
#     res = select(self.model).select_from(self.model).outerjoin(Profile).where(
#         Profile.vless_key_id == None, self.model.is_active == True,
#         self.model.server_id != vless_key.server_id).limit(1)
#     response = await db.execute(res)
#     obj = response.scalar()
#     if not obj:
#         return None, self.no_keys_available, None
#     return obj, 0, None
#
#
# async def get_quantity_free_keys(self, *, db: AsyncSession):
#     """Выводит количество свободных ключей"""
#     res = select(self.model).select_from(self.model).outerjoin(Profile).where(
#         Profile.vless_key_id == None, self.model.is_active == True)
#     response = await db.execute(res)
#     quantity_free_keys = len(response.all())
#     return quantity_free_keys, 0, None
