import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# from core.errors import SchemasError
from ip_address.models import IpAddress
from ip_address.shcemas import IpAddressCreate, IpAddressUpdate
from core.base_crud import CRUDBase


class CrudIpAddress(CRUDBase[IpAddress, IpAddressCreate, IpAddressUpdate]):
    # test_error_2 = SchemasError(num=403, message="Not found ip address with this id")
    not_found_id = {"num": 404, "message": "Not found ip address with this id"}
    name_is_exist = {"num": 403, "message": "А ip address with that name already exists"}

    async def get_ip_address_by_id(self, *, db: AsyncSession, ip_address_id: int):
        obj = await super().get(db=db, id=ip_address_id)
        if obj is None:
            return None, self.not_found_id, None
        return obj, 0, None

    async def get_all_ips_addresses(self, *, db: AsyncSession, skip: int, limit: int):
        objects = await super().get_multi(db_session=db, skip=skip, limit=limit)
        return objects, 0, None

    async def add_ip_address(self, *, db: AsyncSession, new_data: IpAddressCreate):
        # check name
        query = select(self.model).where(self.model.name == new_data.name)
        response = await db.execute(query)
        if response.scalar_one_or_none() is not None:
            return None, self.name_is_exist, None
        objects = await super().create(db_session=db, obj_in=new_data)
        return objects, 0, None

    async def update_ip_address(self, *, db: AsyncSession, update_data: IpAddressUpdate, ip_address_id: int):
        # check id
        query = select(self.model).where(self.model.id == ip_address_id)
        resp = await db.execute(query)
        this_obj = resp.scalar_one_or_none()
        if this_obj is None:
            return None, self.not_found_id, None
        # check name
        if update_data.name is not None:
            query = select(self.model).where(self.model.name == update_data.name, self.model.id != ip_address_id)
            response = await db.execute(query)
            if response.scalar_one_or_none() is not None:
                return None, self.name_is_exist, None
        objects = await super().update(db_session=db, obj_current=this_obj, obj_new=update_data)
        return objects, 0, None


crud_ip_address = CrudIpAddress(IpAddress)
