from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_crud import CRUDBase
from outline.outline.outline_vpn.outline_vpn import OutlineVPN
from server.models import Server
from server.schemas import ServerCreate, ServerUpdate


class CrudServer(CRUDBase[Server, ServerCreate, ServerUpdate]):
    obj_name = "Server"
    not_found_id = {"num": 404, "message": f"Not found {obj_name} with this id"}
    name_is_exist = {"num": 403, "message": f"А {obj_name} with that name already exists"}
    address_is_exist = {"num": 403, "message": f"А {obj_name} with that address already exists"}
    no_good_server = {"num": 403, "message": f"There is not a single free space on the servers"}
    id_is_exist = {"num": 403, "message": f"А {obj_name} with that id already exists"}

    async def get_server_by_id(self, *, db: AsyncSession, id: int):
        obj = await super().get(db=db, id=id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def get_all_servers(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

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

    async def get_good_server(self, *, db: AsyncSession):
        # дописать проверку на is_active
        objects = await super().get_multi(db_session=db, skip=0, limit=10000)
        try:
            for server in objects:
                client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
                fact_client = len(client.get_keys())
                if fact_client <= server.max_client:
                    return server, 0, None
            return None, self.no_good_server, None
        except Exception as ex:
            return None, self.outline_error(ex=ex), None

    async def get_replacement_server(self, *, db: AsyncSession, server_id: int):
        query = select(self.model).where(self.model.id != server_id, self.model.is_active != False)
        response = await db.execute(query)
        good_servers = response.scalars().all()
        if not good_servers:
            return None, self.no_good_server, None
        elif good_servers is not None:
            for server in good_servers:
                try:
                    print(server.id)
                    client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
                    fact_client = len(client.get_keys())
                    print(fact_client)
                    if fact_client <= server.max_client:
                        return server, 0, None
                except:
                    pass
            return None, self.no_good_server, None


crud_server = CrudServer(Server)
