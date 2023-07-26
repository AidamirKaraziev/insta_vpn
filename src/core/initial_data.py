from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from role.models import Role
from old_code.order_status.models import Status
from database import get_async_session


async def check_roles(session: AsyncSession = Depends(get_async_session)):
    # Проверяем наличие ролей
    query_admin = select(Role).where(Role.name == 'admin', Role.id == 1)
    query_user = select(Role).where(Role.name == 'user', Role.id == 2)

    admin_role = await session.execute(query_admin)
    user_role = await session.execute(query_user)

    if admin_role.scalar_one_or_none() is not None:
        admin_role_is_exist = True
    else:
        admin_role_is_exist = False

    if user_role.scalar_one_or_none() is not None:
        user_role_is_exist = True
    else:
        user_role_is_exist = False

    return admin_role_is_exist, user_role_is_exist


async def check_order_statuses(session: AsyncSession = Depends(get_async_session)):
    # Проверям наличие статуслов
    query_created = select(Status).where(Status.name == 'created', Status.id == 1)
    query_in_progress = select(Status).where(Status.name == 'in_progress', Status.id == 2)
    query_completed = select(Status).where(Status.name == 'completed', Status.id == 3)

    status_created = await session.execute(query_created)
    status_in_progress = await session.execute(query_in_progress)
    status_completed = await session.execute(query_completed)
    statuses = [status_created, status_in_progress, status_completed]

    result = []
    for status in statuses:
        if status.scalar_one_or_none() is not None:
            result.append(True)
        else:
            result.append(False)

    return result


async def create_statuses():
    async for db in get_async_session():
        statuses = []

        statuses_is_exist = await check_order_statuses(db)
        if statuses_is_exist[0] and statuses_is_exist[1] and statuses_is_exist[2]:
            return  # Начальные данные уже существуют

        if not statuses_is_exist[0]:
            statuses.append(Status(id=1, name='created'))
        if not statuses_is_exist[1]:
            statuses.append(Status(id=2, name='in_progress'))
        if not statuses_is_exist[2]:
            statuses.append(Status(id=3, name='completed'))

        [db.add(status) for status in statuses]
        await db.commit()
        await db.close()


async def create_roles():
    async for db in get_async_session():
        roles = []

        # Проверка наличия данных
        admin_role_is_exist, user_role_is_exist = await check_roles(db)

        if admin_role_is_exist and user_role_is_exist:
            return  # Начальные данные уже существуют

        # Создание недостающих ролей
        if not admin_role_is_exist:
            roles.append(Role(id=1, name='admin'))
        if not user_role_is_exist:
            roles.append(Role(id=2, name='user'))

        [db.add(role) for role in roles]
        await db.commit()
        await db.close()


async def create_initial_data():
    await create_roles()
    # await create_statuses()
