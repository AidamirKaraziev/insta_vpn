from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database import get_async_session
from partner.models import Partner
from referent_type.models import ReferentType
from status.models import Status
from tariff.models import Tariff
from vpn_type.models import VpnType


async def check_vpn_type(session: AsyncSession = Depends(get_async_session)):
    check_list = [
        VpnType(id=1, name='Outline'),
        VpnType(id=2, name='VLESS')]

    creation_list = []
    for obj in check_list:
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
    check_list = [
        Tariff(id=1, name='30 дней (100₽)', price=100, period_days=30, photo_url='https://i.imgur.com/e4pGpmu.jpg',
               is_active=True),
        Tariff(id=2, name='60 дней (200₽)', price=200, period_days=60, photo_url='https://i.imgur.com/nld6nHb.jpg',
               is_active=True),
        Tariff(id=3, name='90 дней (300₽)', price=300, period_days=90, photo_url='https://i.imgur.com/jEcEWNj.jpg',
               is_active=True)]

    creation_list = []
    for obj in check_list:
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


async def check_partner(session: AsyncSession = Depends(get_async_session)):
    check_list = [Partner(id=1, name='Общие'),
                  Partner(id=2, name='Айдамир'),
                  Partner(id=3, name='Азамат'),
                  Partner(id=4, name='Настя'),
                  Partner(id=5, name='Кара')
                  ]

    creation_list = []
    for obj in check_list:
        query = select(Partner).where(Partner.name == obj.name, Partner.id == obj.id)
        obj_type = await session.execute(query)
        if obj_type.scalar_one_or_none() is None:
            creation_list.append(obj)
    return creation_list


async def create_partner():
    async for db in get_async_session():
        creation_list = await check_partner(db)
        [db.add(obj) for obj in creation_list]
        await db.commit()
        await db.close()


async def check_status(session: AsyncSession = Depends(get_async_session)):
    check_list = [Status(id=1, name='Создан'),
                  Status(id=2, name='Выполняется'),
                  Status(id=3, name='Готово')
                  ]

    creation_list = []
    for obj in check_list:
        query = select(Status).where(Status.name == obj.name, Status.id == obj.id)
        obj_type = await session.execute(query)
        if obj_type.scalar_one_or_none() is None:
            creation_list.append(obj)
    return creation_list


async def create_status():
    async for db in get_async_session():
        creation_list = await check_status(db)
        [db.add(obj) for obj in creation_list]
        await db.commit()
        await db.close()


async def check_referent_type(session: AsyncSession = Depends(get_async_session)):
    check_list = [ReferentType(id=1, name='Native'),
                  ReferentType(id=2, name='Blogger')]

    creation_list = []
    for obj in check_list:
        query = select(ReferentType).where(ReferentType.name == obj.name, ReferentType.id == obj.id)
        obj_type = await session.execute(query)
        if obj_type.scalar_one_or_none() is None:
            creation_list.append(obj)
    return creation_list


async def create_referent_type():
    async for db in get_async_session():
        creation_list = await check_referent_type(db)
        [db.add(obj) for obj in creation_list]
        await db.commit()
        await db.close()


async def create_initial_data():
    try:
        await create_vpn_type()
    except Exception as ex:
        print(ex)
    try:
        await create_tariff()
    except Exception as ex:
        print(ex)
    try:
        await create_partner()
    except Exception as ex:
        print(ex)
    try:
        await create_status()
    except Exception as ex:
        print(ex)
    try:
        await create_referent_type()
    except Exception as ex:
        print(ex)