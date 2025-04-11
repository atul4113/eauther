import os
import sys
import datetime
import mimetypes
from djangae.settings_base import *  # Set up some AppEngine specific stuff
from src.lorepo.app_identity import mock_get_application_id
from src.shared_settings import SHARED_SETTINGS
from lxml import etree
from pathlib import Path
import pymysql

try:
    from .datastore_settings import *
except ImportError:
    pass


pymysql.install_as_MySQLdb()
# Build paths inside the project like this: BASE_DIR / 'subdir'.


BASE_DIR = Path(__file__).resolve().parent.parent

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\Moro\\Work\\atul_last_updated\\eauther\\src\\key.json"
os.environ["DATASTORE_PROJECT_ID"]="eauthor-dev"
os.environ["CLOUDSDK_CORE_PROJECT"]="eauthor-dev"
DJANGAE_INDEX_YAML = 'djangaeidx.yaml'
# os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8081"
# os.environ["DATASTORE_PROJECT_ID"] = "ealpha-test-application"
# os.environ["CLOUDSDK_CORE_PROJECT"] = "ealpha-test-application"
# os.environ["CLOUDSDK_API_ENDPOINT_OVERRIDES_DATASTORE"] = "http://localhost:8081/"

# os.environ["GOOGLE_CLOUD_DISABLE_GRPC"] = "True"


APPLICATION_ID = mock_get_application_id()

APP_NAME = SHARED_SETTINGS[APPLICATION_ID]['app_name']
SERVER_URL = SHARED_SETTINGS[APPLICATION_ID]['server_url']
BASE_URL = SHARED_SETTINGS[APPLICATION_ID]['base_url']
MAUTHOR_BASIC_URL = SHARED_SETTINGS[APPLICATION_ID]['base_secure_url']

DATABASES = {
    "default": {
        "ENGINE": "gcloudc.db.backends.datastore",
        'TEST': {
            'GENERATE_SPECIAL_INDEXES': True
        },
        "PROJECT": os.getenv("DATASTORE_PROJECT_ID", "ealpha-test-application"),
        'INDEXES_FILE': 'indexes.json',
        "NAMESPACE": "",  # Optional namespace
    }
}
 
if "DATASTORE_EMULATOR_HOST" in os.environ:
    os.environ["DATASTORE_EMULATOR_HOST"] = os.getenv("DATASTORE_EMULATOR_HOST").strip()
 


HTTPS_REDIRECT = SHARED_SETTINGS[APPLICATION_ID]['https_redirect']
SECRET_KEY = SHARED_SETTINGS[APPLICATION_ID]['secret_key']
MAUTHOR_IMPORT_SECRET_KEY = ''

RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
NOCAPTCHA = True

USE_I18N = False
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'UTC'

DEBUG = True
DJANGAE_DISABLE_CONSTRAINT_CHECKS = True

INSTALLED_APPS = [
    'djangae', # Djangae needs to come before django apps in django 1.7 and above
    'src.markdown_deux',
    'src.mauthor',
    'drf_spectacular',
    'django.contrib.admin',
    # 'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    # 'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'src.autoload',
    # 'search',
    'src.filetransfers',
    'src.registration',
    'src.remember_me',
    'src.country_utils',
    # Cross-origin resource sharing library: https://github.com/ottoyiu/django-cors-headers
    'src.corsheaders',
    'src.lorepo.assets',
    'src.lorepo.editor',
    'src.lorepo.embed',
    'src.lorepo.home',
    'src.lorepo.labels',
    'src.lorepo.mycontent',
    'src.lorepo.public',
    'src.lorepo.spaces',
    'src.lorepo.support',
    'src.lorepo.newsletter',
    'src.lorepo.user',
    'src.lorepo.filestorage',
    'src.lorepo.cron',
    'src.lorepo.corporate',
    'src.lorepo.permission',
    'src.lorepo.exchange',
    'src.lorepo.course',
    'src.lorepo.token',
    'src.lorepo.translations',
    'src.lorepo.global_settings',
    'src.lorepo.util',
    'src.mauthor.customfixdb',
    'src.mauthor.backup',
    'src.mauthor.bug_track',
    'src.mauthor.bulk',
    'src.mauthor.company',
    'src.mauthor.exchange_narration',
    'src.mauthor.indesign',
    'src.mauthor.localization',
    'src.mauthor.metadata',
    'src.mauthor.pdfimport',
    'src.mauthor.search',
    'src.mauthor.states',
    'src.mauthor.lessons_parsers',
    'src.libraries.logger',
    'src.libraries.testing',
    'src.libraries.utility',
    'src.libraries.wiki',
    'src.captcha',
    'rest_framework_docs',
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
MIDDLEWARE_CLASSES = [
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
]

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
# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis as the message broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Store task results in Redis
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'  # Set the timezone for Celery tasks
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True  # Add this line

ALLOWED_HOSTS = ['*']
SITE_ID = 1
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
                # 'django.core.context_processors.i18n',
                # 'django.core.context_processors.request',
                'django.template.context_processors.request',
                # 'django.core.context_processors.media',
                'django.contrib.messages.context_processors.messages',
                'lorepo.context_processors.settings',
                'lorepo.context_processors.urls',
            ],
        },
    },
]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]
CSRF_COOKIE_HTTPONLY = False
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'UNICODE_JSON': False,
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),  # Accept both formats
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=1),
    'JWT_ALLOW_REFRESH': True,
}

REST_FRAMEWORK_DOCS = {
    'HIDE_DOCS': False  # not is_development_server()
}

SECURE_CHECKS = [

]
SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API',
    'DESCRIPTION': 'Your API description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
    },
}
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'rest_framework_simplejwt.authentication.JWTAuthentication',
]

# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# NOSE_ARGS = ['--with-xunit', '--xunit-file=website-corporate/test-reports/xunit.xml', '-v']
# NOSE_PLUGINS = ['libraries.utility.noseplugins.TestDiscoveryPlugin']
# APPEND_SLASH = False

ADMIN_MEDIA_PREFIX = '/media/admin/'

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

ROOT_URLCONF = 'src.urls'

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
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}


# GCLOUD = {
#     'UNIQUE_CONSTRAINT_CHECKS': 'transactionless',
#     'TRANSACTION_MODE': 'none',  # Explicitly disable transactions
# }


# DEBUG_PROPAGATE_EXCEPTIONS = True


LANGUAGE_CODE = 'en'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
CORS_URLS_REGEX = r'(^/doc/api/.*$)|(^/file/serve/.*$)|(^/api/.*$)'
CORS_ORIGIN_REGEX_WHITELIST = (
    # mAuthor
    r'^(https?://)?(localhost|127\.0\.0\.1):4200$',
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

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse'
#         }
#     },
#     'handlers': {
#         'log_error_message': {
#             'level': 'ERROR',
#             'filters': ['require_debug_false'],
#             'class': 'src.mauthor.admin.log.LogAdminEmailHandler'
#         },
#         'mail_admins': {
#             'level': 'ERROR',
#             'filters': ['require_debug_false'],
#             'class': 'django.utils.log.AdminEmailHandler'
#         },
#         'empty-handler': {
#             'class': 'logging.NullHandler',
#         },
#     },
#     'loggers': {
#         # Silence SuspiciousOperation.DisallowedHost exception ('Invalid
#         # HTTP_HOST' header messages). Set the handler to 'null' so we don't
#         # get those annoying emails.
#         'django.security.DisallowedHost': {
#             'handlers': ['empty-handler'],
#             'propagate': False,
#         },
#         'django.request': {
#             'handlers': ['log_error_message', 'mail_admins'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     }
# }

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Or your custom backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # For development,

EMAIL_HOST = 'smtp.example.com'  # Your SMTP server
EMAIL_PORT = 587  # Your SMTP port
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'  # Your email address
EMAIL_HOST_PASSWORD = 'your-password'  # Your email password
DEFAULT_FROM_EMAIL = 'noreply@example.com'


def get_bucket_name(name):
    if APPLICATION_ID == 'lorepocorporate':
        return '/' + name

    if APPLICATION_ID == 'mauthor-china':
        return '/china-' + name

    return '/' + APPLICATION_ID + '-' + name

# this is  for django tests, because on jenkins djangae in installed apps
if 'test' in sys.argv[1:] or 'jenkins' in sys.argv[1:]:
    INSTALLED_APPS = INSTALLED_APPS[1:]
