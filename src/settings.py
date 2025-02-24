import os
import sys
import datetime
import mimetypes
from djangae.settings_base import *  # Set up some AppEngine specific stuff
from .lorepo.app_identity import mock_get_application_id
from .shared_settings import SHARED_SETTINGS
import logging
from lxml import etree
# import environ
#
# env = environ.Env()
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print("BASE_DIR", BASE_DIR)
# environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
# file_yaml = env("", default="")
#
# print("DJANGAE_APP_YAML_LOCATION")
# print(os.environ.get("DJANGAE_APP_YAML_LOCATION"), "21212")

APPLICATION_ID = mock_get_application_id()

APP_NAME = SHARED_SETTINGS[APPLICATION_ID]['app_name']
SERVER_URL = SHARED_SETTINGS[APPLICATION_ID]['server_url']
BASE_URL = SHARED_SETTINGS[APPLICATION_ID]['base_url']
MAUTHOR_BASIC_URL = SHARED_SETTINGS[APPLICATION_ID]['base_secure_url']


DATABASES = {
    # 'default': {
    #     'ENGINE': 'djangae.db.backends.appengine'
    # }
    'default': {  
        'ENGINE': 'django.db.backends.mysql',  
        'NAME': 'itilite',  
        'USER': 'itilite',  
        'PASSWORD': 'itilite',  
        'HOST': 'localhost',  
        'PORT': '3306',  
        'OPTIONS': {  
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"  
        }  
    }  
}


HTTPS_REDIRECT = SHARED_SETTINGS[APPLICATION_ID]['https_redirect']
SECRET_KEY = SHARED_SETTINGS[APPLICATION_ID]['secret_key']
MAUTHOR_IMPORT_SECRET_KEY = ''


RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
NOCAPTCHA = True

USE_I18N = False
USE_L10N = True
USE_TZ = False

DJANGAE_DISABLE_CONSTRAINT_CHECKS = True

INSTALLED_APPS = (
    'djangae', # Djangae needs to come before django apps in django 1.7 and above
    'djangae.task',
    'markdown_deux',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    # 'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'autoload',
    # 'search',
    'filetransfers',
    'registration',
    'remember_me',
    'country_utils',
    # Cross-origin resource sharing library: https://github.com/ottoyiu/django-cors-headers
    'corsheaders',
    'lorepo.assets',
    'lorepo.editor',
    'lorepo.embed',
    'lorepo.home',
    'lorepo.labels',
    'lorepo.mycontent',
    'lorepo.public',
    'lorepo.spaces',
    'lorepo.support',
    'lorepo.user',
    'lorepo.filestorage',
    'lorepo.cron',
    'lorepo.corporate',
    'lorepo.permission',
    'lorepo.exchange',
    'lorepo.course',
    'lorepo.token',
    'lorepo.translations',
    'lorepo.global_settings',
    'lorepo.util',
    'mauthor.backup',
    'mauthor.bug_track',
    'mauthor.bulk',
    'mauthor.company',
    'mauthor.exchange_narration',
    'mauthor.indesign',
    'mauthor.localization',
    'mauthor.metadata',
    'mauthor.pdfimport',
    'mauthor.search',
    'mauthor.states',
    'mauthor.lessons_parsers',
    'libraries.logger',
    'libraries.testing',
    'libraries.utility',
    'libraries.wiki',
    'captcha',
    'rest_framework',
    'rest_framework_docs',
)

MIDDLEWARE_CLASSES = (
#    'google.appengine.ext.appstats.recording.AppStatsDjangoMiddleware', # uncomment to enable http://localhost:8000/_ah/stats
#     'autoload.middleware.AutoloadMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'lorepo.corporate.middleware.CorporateMiddleware',
    'lorepo.user.middleware.LoggingMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'lorepo.HTTPSRedirectMiddleware.HTTPSRedirect',
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedSHA1PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

ALLOWED_HOSTS = ['*']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
	    'DIRS': [os.path.join(os.path.dirname(__file__), 'mauthor', 'templates'),
                 os.path.join(os.path.dirname(__file__), 'lorepo', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # 'lorepo.context_processor.settings',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.request',
                'django.template.context_processors.request',
                'django.core.context_processors.media',
                'django.contrib.messages.context_processors.messages',
                'lorepo.context_processors.settings',
                'lorepo.context_processors.urls',
            ],
        },
    },
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'UNICODE_JSON': False,
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=3000)
}

REST_FRAMEWORK_DOCS = {
    'HIDE_DOCS': False  # not is_development_server()
}

SECURE_CHECKS = [

]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', )

# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# NOSE_ARGS = ['--with-xunit', '--xunit-file=website-corporate/test-reports/xunit.xml', '-v']
# NOSE_PLUGINS = ['libraries.utility.noseplugins.TestDiscoveryPlugin']

ADMIN_MEDIA_PREFIX = '/media/admin/'

STATIC_URL = '/media/'

ROOT_URLCONF = 'urls'

ACCOUNT_ACTIVATION_DAYS = 2
LOGIN_REDIRECT_URL = '/corporate'
EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = SHARED_SETTINGS[APPLICATION_ID]['default_from_email']

FLEXIBLE_SERVICE_ACCOUNT = SHARED_SETTINGS[APPLICATION_ID]['flexible_account']
HOME_PAGE = SHARED_SETTINGS[APPLICATION_ID]['home_page']

MATH_CAPTCHA_QUESTION = "Captcha"

LOGO_SIZE = {'width': 230, 'height': 70}

INITIAL_PACKAGE_CONTENT = SHARED_SETTINGS[APPLICATION_ID]['initial_package_content']
LESSON_DEFAULT_ICON = SHARED_SETTINGS[APPLICATION_ID]['lesson_default_icon']

SERVER_EMAIL = SHARED_SETTINGS[APPLICATION_ID]['server_email']
LEARNETIC_EMAIL = SHARED_SETTINGS[APPLICATION_ID]['learnetic_email']

ADMINS = (('Solwit', 'ealpha619@gmail.com'),)

# AUTH_PROFILE_MODULE = "user.UserProfile"

DJANGAE_CACHE_ENABLED = False

# Register common mime types as they may not be available in GAE
mimetypes.add_type('audio/mp3', '.mp3', True)
mimetypes.add_type('audio/ogg', '.ogg', True)
mimetypes.add_type('audio/oga', '.oga', True)
mimetypes.add_type('text/plain', '.txt', True)
mimetypes.add_type('video/mp4', '.mp4', True)
mimetypes.add_type('video/ogg', '.ogv', True)
mimetypes.add_type('video/webm', '.webm', True)
mimetypes.add_type('image/svg+xml', '.svg', True)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'TIMEOUT': 0,
        'VERSION': 10
    }
}

LANGUAGE_CODE = 'en'

gettext_noop = lambda s: s
LANGUAGES = (       #available to administrators
    ('en', gettext_noop('English')),
    ('ar', gettext_noop('Arabic')),
    ('pl', gettext_noop('Polish')),
    ('es', gettext_noop('Spanish')),
    ('fr', gettext_noop('French')),
)

USER_LANGUAGES = [    #available to users
    ('en', 'English')
]

USER_DEFAULT_LANG = 'en_US'

# Cross-Origin Resource Sharing settings
CORS_ORIGIN_ALLOW_ALL = False
CORS_URLS_REGEX = r'(^/doc/api/.*$)|(^/file/serve/.*$)'
CORS_ORIGIN_REGEX_WHITELIST = (
    # mAuthor
    r'^(https?://)?(www\.)?mauthor\.com$',
    r'^(https?://)?([\w\-]+\.?)?mauthor-dev\.appspot\.com$',
    r'^(https?://)?([\w\-]+\.?)?lorepocorporate\.appspot\.com$',
    r'^(https?://)?([\w\-]+\.?)?newinterfaceservice-dot-lorepocorporate\.appspot\.com$',
    r'^(https?://)?([\w\-]+\.?)?new\.mauthor\.com$',
    r'^(https?://)?([\w\-]+\.?)?newinterface\.mauthor\.com$',
    # mInstructor-lnc
    r'^(https?://)?(www\.)?minstructor\.com$',
    r'^(https?://)?([\w\-]+\.?)?minstructor\-lnc\.appspot\.com$',
    # mInstructor-poland
    r'^(https?://)?(www\.)?minstructor\.pl$',
    r'^(https?://)?([\w\-]+\.?)?minstructor\-poland\.appspot\.com$',
    # mInstructor-mexico
    r'^(https?://)?(www\.)?minstructor\.mx',
    r'^(https?://)?([\w\-]+\.?)?minstructor\-mexico\.appspot\.com$',
    # mInstructor-turkey
    r'^(https?://)?([\w\-]+\.?)?minstructor\-turkey\.appspot\.com$',
    # mInstructor-kazakhstan
    r'^(https?://)?(www\.)?minstructor\.kz',
    r'^(https?://)?([\w\-]+\.?)?minstructor\-kazakhstan\.appspot\.com$',
    # mInstructor-saudi-arabia
    r'^(https?://)?(www\.)?ealphainstructor\.info',
    r'^(https?://)?([\w\-]+\.?)?minstructor\-saudi\-arabia\.appspot\.com$',
    # mInstructor-slovakia
    r'^(https?://)?(www\.)?minstructor\.sk',
    r'^(https?://)?([\w\-]+\.?)?minstructor\-slovakia\.appspot\.com$',
    # mInstructor-malaysia
    r'^(https?://)?(www\.)?minstructor\.my',
    r'^(https?://)?([\w\-]+\.?)?minstructor\-malaysia\.appspot\.com$',
    # mInstructor-france
    r'^(https?://)?(www\.)?minstructor\.fr',
    r'^(https?://)?([\w\-]+\.?)?minstructor\-france\.appspot\.com$',
    # mInstructor-philippines
    r'^(https?://)?(www\.)?minstructor\.ph',
    r'^(https?://)?([\w\-]+\.?)?minstructor\-philippines\.appspot\.com$',
    # mInstructor-dev
    r'^(https?://)?([\w\-]+\.?)?minstructor\-dev\.appspot\.com$',
)

lxml_parser_options = {
    "strip_cdata": False,
    "encoding": 'UTF-8'
}
etree.set_default_parser(parser=etree.XMLParser(**lxml_parser_options))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'log_error_message': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'mauthor.admin.log.LogAdminEmailHandler'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'empty-handler': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        # Silence SuspiciousOperation.DisallowedHost exception ('Invalid
        # HTTP_HOST' header messages). Set the handler to 'null' so we don't
        # get those annoying emails.
        'django.security.DisallowedHost': {
            'handlers': ['empty-handler'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['log_error_message', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

EMAIL_BACKEND = 'lorepo.util.email_backend.RecipientsCheckEmailBackend'


def get_bucket_name(name):
    if APPLICATION_ID == 'lorepocorporate':
        return '/' + name

    if APPLICATION_ID == 'mauthor-china':
        return '/china-' + name

    return '/' + APPLICATION_ID + '-' + name

# this is  for django tests, because on jenkins djangae in installed apps
if 'test' in sys.argv[1:] or 'jenkins' in sys.argv[1:]:
    INSTALLED_APPS = INSTALLED_APPS[1:]
