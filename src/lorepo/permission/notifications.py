from src.lorepo.public.util import send_message
import settings

def send_no_access_notification(user, message):
    send_message(settings.SERVER_EMAIL, [user], 'Permission denied', message)