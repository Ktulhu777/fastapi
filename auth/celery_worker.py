import smtplib
from email.message import EmailMessage
from celery import Celery
from config import SMTP_USER, SMTP_PASSWORD

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 465

celery = Celery('tasks', broker='redis://localhost:6379', )


def get_email_template(username: str):
    email = EmailMessage()
    email['Subject'] = "Что то"
    email['From'] = SMTP_USER
    email['To'] = SMTP_USER

    email.set_content(
        f'<h1>Здравствуйте {username}</h1>',
        subtype='html'
    )
    return email


@celery.task
def send_email(username: str):
    email = get_email_template(username)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)
