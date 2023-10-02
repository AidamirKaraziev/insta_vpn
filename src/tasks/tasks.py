import smtplib
from email.message import EmailMessage
from typing import Optional

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession

from config import SMTP_USER, SMTP_PASSWORD, REDIS_HOST, REDIS_PORT
from utils.utils import deactivation_bab_servers

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


# @celery.task
# async def deactivate_servers(db: AsyncSession):
#     servers, code, indexes = await deactivation_bab_servers(db=db)
#     return servers, code, indexes
