
# написать функцию которая будет брать все сервера, проходиться по ним считать сколько клиентов и записывать в базу
# данных
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import LIMIT_SERVERS
from database import get_async_session
from outline.outline.outline_vpn.outline_vpn import OutlineVPN
from profiles.crud import crud_profile
from profiles.schemas import ProfileUpdate
from server.crud import crud_server
from server.schemas import ServerUpdate


def outline_error(ex: Exception):
    return {"num": 403, "message": f"Error in outline Server {ex}"}


# функция по обновлению данных в профилях
async def update_data_in_profiles( db: AsyncSession, skip: int = 0):
    # get all servers
    servers, code, indexes = await crud_server.get_all_servers(db=db, skip=skip, limit=LIMIT_SERVERS)
    not_in_db = []
    in_db = []
    for server in servers:
        try:
            client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
            keys = client.get_keys()
            for key in keys:
                # get profile
                profile, code, indexes = await crud_profile.get_profile_by_key_id_server_id(db=db,
                                                                                            key_id=int(key.key_id),
                                                                                            server_id=int(server.id))
                if indexes is not None:
                    not_in_db.append(indexes)
                if profile is not None:
                    in_db.append(profile)
                    update_data = ProfileUpdate(used_bytes=key.used_bytes)
                    obj, code, indexes = await crud_profile.update_profile(
                        db=db, update_data=update_data, id=profile.id)
                # print(key)
                # print(profile)
                # profile, code, indexes = await crud_profile.update_profile(db=db, id=profile.id)
        except Exception as ex:
            return None, outline_error(ex=ex), None

        # print(not_in_db)
        print("1"*130)
        print(in_db)
        return in_db, 0, None


# max_client
