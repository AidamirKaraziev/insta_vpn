from datetime import datetime
import subprocess

from sqlalchemy.ext.asyncio import AsyncSession

from config import LIMIT_SERVERS, LIMIT_PROFILES, FREE_TRAFFIC, PAYMENT_WAITING_TIME
from outline.outline.outline_vpn.outline_vpn import OutlineVPN
from profiles.crud import crud_profile
from profiles.schemas import ProfileUpdate
from server.crud import crud_server
from server.schemas import ServerUpdate

"""
Какие функции в утилитах?
1. Функция обновления байтов
2. Функция обновления фактического количества на серверах
3. Функция деактивации устаревших профилей
4. Функция удаления устаревших профилей 
5. Функция установки максимального количества клиентов на сервер
6. Функция вывода неработающих серверов 
"""


def outline_error(ex: Exception):
    return {"num": 403, "message": f"Error in outline Server {ex}"}


async def update_used_bytes_in_profiles(db: AsyncSession, skip: int = 0):
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
        except Exception as ex:
            return None, outline_error(ex=ex), None
    return in_db, 0, None


async def update_fact_clients(*, skip: int = 0, db: AsyncSession):
    # get all server
    servers, code, indexes = await crud_server.get_all_servers(db=db, skip=skip, limit=LIMIT_SERVERS)
    for server in servers:
        try:
            client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
            fact_client = len(client.get_keys())
        except Exception as ex:
            return None, outline_error(ex=ex), None
        update_data = ServerUpdate(fact_client=fact_client)
        server, code, indexes = await crud_server.update_server(db=db, id=server.id,
                                                                update_data=update_data)
    return servers, 0, None


async def deactivate_profile(*, db: AsyncSession, skip: int = 0):
    # get all profiles
    profiles, code, indexes = await crud_profile.get_all_profiles(db=db, skip=skip, limit=LIMIT_PROFILES)
    for profile in profiles:
        if profile.date_end <= datetime.date(datetime.now()):
            # add data_limit
            server, code, indexes = await crud_server.get_server_by_id(db=db, id=profile.server_id)
            try:
                client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
                client.add_data_limit(key_id=profile.key_id, limit_bytes=FREE_TRAFFIC)
            except Exception as ex:
                return None, outline_error(ex=ex), None
            update_data = ProfileUpdate(data_limit=FREE_TRAFFIC, is_active=False)
            obj, code, indexes = await crud_profile.update_profile(db=db, update_data=update_data, id=profile.id)
    return profiles, code, indexes


async def deleting_an_outdated_profile(db: AsyncSession):
    # получить profile
    profiles, code, indexes = await crud_profile.get_all_profiles(db=db, skip=0, limit=LIMIT_PROFILES)
    count_prof = len(profiles)
    deleted_prof = 0
    for profile in profiles:
        # calculation time
        date_end = datetime.strptime(str(profile.date_end), '%Y-%m-%d %H:%M:%S.%f%z').date()
        days = datetime.date(datetime.utcnow()) - date_end
        seconds = days.total_seconds()

        if seconds >= PAYMENT_WAITING_TIME:
            # удалить устаревший профиль
            server, code, indexes = await crud_server.get_server_by_id(db=db, id=profile.server_id)
            try:
                client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
                client.delete_key(key_id=profile.key_id)
            except Exception as ex:
                return None, outline_error(ex=ex), None
            pofile, code, indexes = await crud_profile.delete_profile(db=db, id=profile.id)
            deleted_prof = count_prof - 1
    return f"Было: {count_prof} | Стало: {deleted_prof}", 0, None


# TODO сделать асинхронной или удалить
def check_server(servers_address):
    no_online = []
    for server_address in servers_address:
        try:
            # Выполняем ping-запрос
            subprocess.check_output(["ping", "-c", "1", str(server_address.address)])
        except subprocess.CalledProcessError:
            no_online.append(server_address)
    return no_online


# TODO написать функцию которая проверяет работает ли впн
# TODO почистить алембик миграции
"""необходимо написать такую функцию,
которая если если ключ оплачен, но его нет на сервере выдает новый ключ пользователю"""


# TODO написать функцию которая если не пир еще оплачем но на сервере его нет
