import os

from dotenv import load_dotenv

from partner.schemas import PartnerCreate
from referent_type.schemas import ReferentTypeCreate
from status.schemas import StatusCreate
from tariff.schemas import TariffCreate
from vpn_type.schemas import VpnTypeCreate

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_USER_TEST = os.environ.get("DB_USER_TEST")
DB_PASS_TEST = os.environ.get("DB_PASS_TEST")

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")

SECRET_AUTH = os.environ.get("SECRET_AUTH")

SUPERUSER_EMAIL = os.environ.get("SUPERUSER_EMAIL")
SUPERUSER_PASSWORD = os.environ.get("SUPERUSER_PASSWORD")

SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

"""Еще нужны"""
LIMIT_SERVERS = 1000  # Максимальное количество серверов
LIMIT_PROFILES = 10000  # Максимальное количество профилей
MAX_CLIENT = 100  # Максимальное количество клиентов на одном сервере
MAX_PROFILE_TO_ACCOUNT = 5  # Максимальное количество профилей для одного профиля
TRIAL_DAYS = 3  # Количество пробных дней

"""REFERENT"""
BASE_REFERENT_GIFT_DAYS = 4  # базовое количество подарочных дней
BASE_PARTNER = 1  # базовый партнер - лицо привело референта 1="Общие", нужно для KPI
THE_AMOUNT_OF_PAYMENT_FOR_A_REFERRAL = 50  # Реферальная выплата за нового клиента

OUTLINE_USERS_GATEWAY = os.environ.get("OUTLINE_USERS_GATEWAY")
OUTLINE_SALT = os.environ.get("OUTLINE_SALT")
CONN_NAME = os.environ.get("CONN_NAME")

VLESS_USERS_GATEWAY = os.environ.get("VLESS_USERS_GATEWAY")

BASE_REFERRAL_LINK = "https://t.me/financier_tgrm_bot?start="  # bot/referral/uuid

# TODO заменить на бота для референтов
BASE_REGISTER_REFERENT_LINK = "https://t.me/financier_tgrm_bot?start="  # bot/referral/uuid

"""Payment"""
STATUS_CREATE = StatusCreate(id=1, name='Создан')
STATUS_ERROR = StatusCreate(id=2, name='Ошибка')
STATUS_DONE = StatusCreate(id=3, name='Готов')

"""Partner"""
GENERAL_PARTNER = PartnerCreate(id=1, name='Общие')
AIDAMIR_PARTNER = PartnerCreate(id=2, name='Айдамир')
AZAMAT_PARTNER = PartnerCreate(id=3, name='Азамат')
NASTYA_PARTNER = PartnerCreate(id=4, name='Настя')
KARA_PARTNER = PartnerCreate(id=5, name='Кара')

"""ReferentType"""
NATIVE_REFERENT_TYPE = ReferentTypeCreate(id=1, name='Native')
BLOGGER_REFERENT_TYPE = ReferentTypeCreate(id=2, name='Blogger')

"""Tariff"""
ONE_MONTH_TARIFF = TariffCreate(
    id=1, name='30 дней (100₽)', price=100, period_days=30, photo_url='https://i.imgur.com/e4pGpmu.jpg', is_active=True)
TWO_MONTH_TARIFF = TariffCreate(
    id=2, name='60 дней (200₽)', price=200, period_days=60, photo_url='https://i.imgur.com/nld6nHb.jpg', is_active=True)
THREE_MONTH_TARIFF = TariffCreate(
    id=3, name='90 дней (300₽)', price=300, period_days=90, photo_url='https://i.imgur.com/jEcEWNj.jpg', is_active=True)

"""VpnType"""
OUTLINE_VPN_TYPE = VpnTypeCreate(id=1, name='Outline')
VLESS_VPN_TYPE = VpnTypeCreate(id=2, name='VLESS')


"""Уже не нужны"""
FREE_TRAFFIC = 1  # Максимальное количество байт для статического ключа
PAYMENT_WAITING_TIME = 86400 * 2  # 1 day = 86400 РУДИМЕНТ -> УДАЛИТЬ
