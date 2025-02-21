import settings
from django.template import loader
from django.template.context import Context
from lorepo.exchange.models import ExportVersions
from mauthor.metadata.util import get_metadata_values
import hashlib
from settings import MAUTHOR_IMPORT_SECRET_KEY
from cloudstorage import ForbiddenError
from google.appengine.api.urlfetch_errors import InternalTransientError
from google.appengine.ext.blobstore import InternalError
from google.appengine.runtime.apiproxy_errors import OverQuotaError, DeadlineExceededError


RETRY_ERRORS = (InternalTransientError,
                OverQuotaError,
                DeadlineExceededError,
                ForbiddenError,
                InternalError,
                )


def render_manifest(content, version=ExportVersions.SCORM_2004.type):
    template = 'initdata/scorm/imsmanifest_2004.xml' if int(version) == ExportVersions.SCORM_2004.type else 'initdata/scorm/imsmanifest_1_2.xml'
    template = loader.get_template(template)
    extended_metadata = get_metadata_values(content)
    context = Context({'content': content, 'passing_score': content.passing_score/100, 'extended_metadata': extended_metadata, 'settings': settings})
    return template.render(context)


def make_secret(content_id, session_id):
    return str(hashlib.md5("%s%s%s" % (content_id, MAUTHOR_IMPORT_SECRET_KEY, session_id)).hexdigest())