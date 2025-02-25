import settings
from django.template import loader
from django.template.context import Context
from lorepo.exchange.models import ExportVersions
from mauthor.metadata.util import get_metadata_values
import hashlib
from settings import MAUTHOR_IMPORT_SECRET_KEY
from google.cloud import storage  # For cloud storage operations
from requests.exceptions import RequestException  # Replace urlfetch errors with requests exceptions
class ForbiddenError(Exception):
    """Custom exception to handle forbidden errors."""
    pass

# Replace specific Google Cloud errors with generic Python exceptions or requests exceptions
RETRY_ERRORS = (RequestException,  # This covers common network-related errors
                ForbiddenError,  # Custom error class, should be defined elsewhere or replaced by a generic exception
                )


def render_manifest(content, version=ExportVersions.SCORM_2004.type):
    # Selecting the template based on the SCORM version
    template = 'initdata/scorm/imsmanifest_2004.xml' if int(
        version) == ExportVersions.SCORM_2004.type else 'initdata/scorm/imsmanifest_1_2.xml'
    template = loader.get_template(template)
    extended_metadata = get_metadata_values(content)

    # Rendering the context with content and settings
    context = Context({
        'content': content,
        'passing_score': content.passing_score / 100,
        'extended_metadata': extended_metadata,
        'settings': settings
    })

    return template.render(context)


def make_secret(content_id, session_id):
    # Creating a secret hash from content ID, session ID, and the secret key
    secret = "%s%s%s" % (content_id, MAUTHOR_IMPORT_SECRET_KEY, session_id)
    return hashlib.md5(secret.encode('utf-8')).hexdigest()

