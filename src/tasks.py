# tasks.py
from .celery import shared_task

@shared_task
def add(x, y):
    return x + y

@shared_task
def send_email():
    # Simulate sending an email
    print("Sending email...")
    return "Email sent!"