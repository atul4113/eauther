# Load the siteconf module
from django.conf import settings
from importlib import import_module
SITECONF_MODULE = getattr(settings, 'AUTOLOAD_SITECONF', settings.ROOT_URLCONF)
import_module(SITECONF_MODULE)
