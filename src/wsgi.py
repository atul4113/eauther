"""
WSGI config for scaffold project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""


from .lorepo.boot import fix_path
fix_path()

from django.core.wsgi import get_wsgi_application
from djangae.utils import on_production

settings = "settings_live" if on_production() else "settings"
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

from djangae.wsgi import DjangaeApplication

application = DjangaeApplication(get_wsgi_application())
