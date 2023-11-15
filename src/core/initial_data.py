from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database import get_async_session
from tariff.models import Tariff
from vpn_type.models import VpnType


async def check_vpn_type(session: AsyncSession = Depends(get_async_session)):
    outline_vpn_type = VpnType(id=1, name='Outline')
    vless_vpn_type = VpnType(id=2, name='VLESS')
    vpn_type_check_list = [outline_vpn_type, vless_vpn_type]

    creation_list = []
    for obj in vpn_type_check_list:
        query = select(VpnType).where(VpnType.name == obj.name, VpnType.id == obj.id)
        obj_type = await session.execute(query)
        if obj_type.scalar_one_or_none() is None:
            creation_list.append(obj)
    return creation_list


async def create_vpn_type():
    async for db in get_async_session():
        creation_list = await check_vpn_type(db)
        [db.add(obj) for obj in creation_list]
        await db.commit()
        await db.close()


async def check_tariff(session: AsyncSession = Depends(get_async_session)):
    tariff_check_list = [
        Tariff(id=1, name='30 дней (100₽)', price=100, period_days=30, photo_url='https://i.imgur.com/e4pGpmu.jpg',
               is_active=True),
        Tariff(id=2, name='60 дней (200₽)', price=200, period_days=60, photo_url='https://i.imgur.com/nld6nHb.jpg',
               is_active=True),
        Tariff(id=3, name='90 дней (300₽)', price=300, period_days=90, photo_url='https://i.imgur.com/jEcEWNj.jpg',
               is_active=True)]

    creation_list = []
    for obj in tariff_check_list:
        query = select(Tariff).where(
            Tariff.id == obj.id, Tariff.name == obj.name, Tariff.price == obj.price,
            Tariff.period_days == obj.period_days, Tariff.photo_url == obj.photo_url, Tariff.is_active == obj.is_active)
        obj_tariff = await session.execute(query)
        if obj_tariff.scalar_one_or_none() is None:
            creation_list.append(obj)
    return creation_list


async def create_tariff():
    async for db in get_async_session():
        creation_list = await check_tariff(db)
        [db.add(obj) for obj in creation_list]
        await db.commit()
        await db.close()


async def create_initial_data():
    await create_vpn_type()
    await create_tariff()
