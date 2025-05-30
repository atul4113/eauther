from .settings import *

SESSION_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 2592000 #30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True



JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=300)
}

DJANGAE_ADDITIONAL_MODULES = [ "backup.yaml", "download.yaml", "localization.yaml" ]

SECURE_REDIRECT_EXEMPT = [
    # App Engine doesn't use HTTPS internally, so the /_ah/.* URLs need to be exempt.
    # djangosecure compares these to request.path.lstrip("/"), hence the lack of preceding /
    r"^_ah/"
]

SECURE_CHECKS += ["checks.check_csp_sources_not_unsafe"]

DEBUG = False
TEMPLATE_DEBUG = False
