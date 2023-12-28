from datetime import datetime, date
import subprocess

from sqlalchemy.ext.asyncio import AsyncSession

from config import LIMIT_SERVERS, LIMIT_PROFILES, FREE_TRAFFIC, PAYMENT_WAITING_TIME
from outline.outline.outline_vpn.outline_vpn import OutlineVPN
from profiles.crud import crud_profile
from profiles.schemas import ProfileUpdate
from server.crud import crud_server, check_server_availability
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


async def update_fact_clients(*, db: AsyncSession):
    # get all server
    bad_servers = {}
    good_servers = []
    servers, code, indexes = await crud_server.get_active_servers(db=db)

    for server in servers:
        if await check_server_availability(server.address):
            try:
                client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
                fact_client = len(client.get_keys())
                update_data = ServerUpdate(fact_client=fact_client)
                server, code, indexes = await crud_server.update_server(db=db, id=server.id,
                                                                        update_data=update_data)
                good_servers.append(server)
            except Exception as ex:
                bad_servers[f"{server.id}, {server.name}"] = f"{ex}"
    good_servers.append(bad_servers)
    return good_servers, 0, None


async def deleting_an_outdated_profile(db: AsyncSession):
    # получить profile
    profiles, code, indexes = await crud_profile.get_all_profiles(db=db, skip=0, limit=LIMIT_PROFILES)
    deleted_profiles = []
    for profile in profiles:
        # calculation time
        if isinstance(profile.date_end, datetime):
            days = date.today() - profile.date_end.date()
        else:
            date_end = datetime.strptime(str(profile.date_end), '%Y-%m-%d %H:%M:%S').date()
            days = date.today() - date_end

        # date_end = datetime.strptime(str(profile.date_end), '%Y-%m-%d %H:%M:%S').date()
        # days = datetime.date(datetime.utcnow()) - date_end
        seconds = days.total_seconds()

        if seconds >= PAYMENT_WAITING_TIME:
            # удалить устаревший профиль
            server, code, indexes = await crud_server.get_server_by_id(db=db, id=profile.server_id)
            try:
                client = OutlineVPN(api_url=server.api_url, cert_sha256=server.cert_sha256)
                deleted = client.delete_key(key_id=profile.key_id)
                if deleted is True:
                    deleted_profiles.append(profile.id)
                    pofile, code, indexes = await crud_profile.delete_profile(db=db, id=profile.id)
                    if code != 0:
                        return None, code, None
            except Exception as ex:
                pass
    return f"Удалил профили: {deleted_profiles} | В количестве: {len(deleted_profiles)}", 0, None


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


async def deactivation_bab_servers(db=AsyncSession, ):
    servers, code, indexes = await crud_server.get_active_servers(db=db)

    for server in servers:
        res = await check_server_availability(server.address)
        if not res:
            update_data = ServerUpdate(is_active=False)
            obj, code, indexes = await crud_server.update_server(db=db, id=server.id, update_data=update_data)
    print(f"Отложенная задача по деактивации плохих серверов выполнена")
