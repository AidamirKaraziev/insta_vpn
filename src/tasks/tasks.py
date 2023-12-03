import asyncio
import logging
from datetime import datetime
from email.message import EmailMessage
from typing import Optional
import smtplib

from pydantic import UUID4
from sqlalchemy import update

from celery import Celery

from profiles.models import Profile
from database import async_session_maker
from config import SMTP_USER, SMTP_PASSWORD, REDIS_HOST, REDIS_PORT
from referent.crud import crud_referent

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

celery = Celery('tasks', broker=f'redis://{REDIS_HOST}:{REDIS_PORT}')


def get_email_template_forgot_password(name: str, email_to: Optional[str], token: str):
    email = EmailMessage()
    email['Subject'] = 'Токен для смены пароля'
    email['From'] = SMTP_USER
    email['TO'] = email_to

    email.set_content(
        '<div>'
        f'<h1 style="color: black;">Здравствуйте, {name}, а вот и ваш токен. Зацените 😊</h1>'
        f'<h3 style="color: blue;">{token}</h3>'
        f'<h3 style="color: black;">Скопируйте его и вставьте в мобильном приложении, чтобы спросить свой пароль!</h3>'
        '<-management-dashboard-ui-design-template-suitable-designing-application-for-android-and-ios-clean-style-app'
        '-mobile-free-vector.jpg" width="600">'
        '</div>',
        subtype='html'
    )

    return email


def get_email_template_request_verify(name: str, email_to: Optional[str], token: str):
    email = EmailMessage()
    email['Subject'] = 'Токен для верификации'
    email['From'] = SMTP_USER
    email['TO'] = email_to

    email.set_content(
        '<div>'
        f'<h1 style="color: black;">Здравствуйте, {name}, а вот и ваш токен. Зацените 😊</h1>'
        f'<h2 style="color: blue;">{token}</h2>'
        f'<h3 style="color: black;">Скопируйте его и вставьте в мобильном приложении, чтобы пройти верификацию!</h3>'
        '<-management-dashboard-ui-design-template-suitable-designing-application-for-android-and-ios-clean-style-app'
        '-mobile-free-vector.jpg" width="600">'
        '</div>',
        subtype='html'
    )
    return email


# TODO добавить отправку уведомления в телеграмм
async def update_fields_is_active():
    today = datetime.now()
    async with async_session_maker() as session:
        query = update(Profile).where(
            Profile.date_end < today, Profile.is_active == True).values(is_active=False, outline_key_id=None)
        await session.execute(query)
        await session.commit()


@celery.task
def send_email_report_forgot_password(token: str, name: str, email_to: str):
    email = get_email_template_forgot_password(token=token, name=name, email_to=email_to)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)


@celery.task
def send_email_request_verify(token: str, name: str, email_to: str):
    email = get_email_template_request_verify(token=token, name=name, email_to=email_to)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)


@celery.task
def describe_profiles():
    asyncio.run(update_fields_is_active())


# TODO написать задачу которая проходится по всем payment
"""
Задача которая проходится по всем payment, где status_id == 1(Создан)
после выполнения:
obj, code, indexes = await crud_referent.change_balance(db=session, id=referent_id, amount=amount)
менять Payment.status_id = 3(Готово)
Если ошибка поменять Payment.status_id = 4(Отказано) - еще не внедрил
"""


@celery.task
async def change_balance_for_referent(referent_id: UUID4, amount: int):
    """
        referent_id: UUID4
        amount: int ; 50(пополнение), -50(списание).
        Отложенный перезапуск в случае неудачи, через count_down. -> запись в лог.
    """
    async with async_session_maker() as session:
        obj, code, indexes = await crud_referent.change_balance(db=session, id=referent_id, amount=amount)
        print(amount)
        if code != 0:
            logging.info('Running...')
            # вот тут надо отложенный перезапуск

