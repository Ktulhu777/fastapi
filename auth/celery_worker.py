import smtplib
from datetime import timedelta
from email.message import EmailMessage
from random import randint
from redis import Redis
from celery import Celery

from config import SMTP_USER, SMTP_PASSWORD

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 465

celery = Celery('tasks', broker='redis://localhost:6379')
celery.broker_connection_retry_on_startup = True
redis = Redis()


def generate_code(username):
    list_number = [str(randint(0, 9)) for _ in range(6)]
    code = "".join(list_number)
    redis.setex(name=username, time=timedelta(minutes=30), value=code)
    return code


def get_email_template(username: str, user_email: str):
    email = EmailMessage()
    email['Subject'] = "Что то"
    email['From'] = SMTP_USER
    email['To'] = user_email

    email.set_content(
        f'''<h1>Здравствуйте {username}</h1>
                <h1>Ваш код {generate_code(username)}</h1>''',
        subtype='html'
    )
    return email


@celery.task
def send_email(username: str, user_email: str):
    email = get_email_template(username, user_email)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)
