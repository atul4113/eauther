from src.lorepo.public.util import send_message
from src import settings

def send_no_access_notification(user, message):
    send_message(settings.SERVER_EMAIL, [user], 'Permission denied', message)