from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_crud import CRUDBase
from core.raise_template import raise_schemas

from outline.outline.outline_vpn.outline_vpn import OutlineVPN
from server.crud import crud_server
from static_key.models import StaticKey
from static_key.schemas import StaticKeyUpdate, StaticKeyCreate


class CrudStaticKey(CRUDBase[StaticKey, StaticKeyCreate, StaticKeyUpdate]):
    obj_name = "StaticKey"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}
    # not_found_by_key_id_server_id = {"num": 404, "message": f"Not found a {obj_name} with this key_id and server_id"}
    not_found_by_server_id = {"num": 404, "message": f"Not found a {obj_name + 's'} with this server_id"}

    async def get_all_static_keys(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def get_static_key_by_id(self, *, db: AsyncSession, id: int):
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def create_key(self, *, db: AsyncSession, server_id: int):
        server, code, indexes = await crud_server.get_server_by_id(db=db, id=server_id)
        if code != 0:
            return None, code, None
        try:
            client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
            key = client.create_key()
            new_data = StaticKeyCreate(server_id=server_id, key_id=key.key_id, name=key.name, port=key.port,
                                       method=key.method, access_url=key.access_url, used_bytes=key.used_bytes,
                                       data_limit=key.data_limit, password=key.password, is_active=True)
            objects = await super().create(db_session=db, obj_in=new_data)
        except Exception as ex:
            return None, raise_schemas(ex), None
        return objects, 0, None

    async def get_static_keys_by_server_id(self, *, db: AsyncSession, server_id: int):
        server, code, indexes = await crud_server.get_server_by_id(db=db, id=server_id)
        if code != 0:
            return None, code, None
        query = select(self.model).where(self.model.server_id == server_id)
        response = await db.execute(query)
        obj = response.scalars().all()
        return obj, 0, None

    async def creating_keys_for_a_server(self, *, db: AsyncSession, server_id: int):
        server, code, indexes = await crud_server.get_server_by_id(db=db, id=server_id)
        if code != 0:
            return None, code, None
        client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
        much_to_create = server.max_client - int(len(client.get_keys()))
        for i in range(much_to_create):
            key, code, indexes = await self.create_key(db=db, server_id=server_id)
            if code != 0:
                return None, code, None
        keys, code, indexes = await self.get_static_key_by_id(db=db, id=server_id)
        return keys, 0, None


crud_static_key = CrudStaticKey(StaticKey)