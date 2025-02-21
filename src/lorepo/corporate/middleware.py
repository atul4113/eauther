from lorepo.permission.util import get_company_for_user
from lorepo.corporate.models import CorporatePublicSpace, CompanyProperties
import libraries.utility.cacheproxy as cache
import re

USER_SPACES_CACHE_TIME = 60 * 60 * 24

SKIPPED_URLS = re.compile('(^/file.*|^/editor/api/blobUploadDir$|^/proxy/get)')


class CorporateMiddleware(object):
    def process_request(self, request):
        request.user.company = None
        request.user.public_category = None
        request.user.divisions = {}

        if SKIPPED_URLS.match(request.path):
            return None

        if not request.user.is_authenticated():
            return None

        company = cache.get_for_user(request.user, 'company')
        public_category = cache.get_for_user(request.user, 'public_category')
        divisions = cache.get_for_user(request.user, 'divisions')
        language_code_bidi = cache.get_for_user(request.user, 'language_code_bidi')
        if company is None \
                or public_category is None \
                or divisions is None \
                or language_code_bidi is None:
            company, public_category, divisions, language_code = self._read_company(request)
            cache.set_for_user(request.user, 'company', company, USER_SPACES_CACHE_TIME)
            cache.set_for_user(request.user, 'public_category', public_category, USER_SPACES_CACHE_TIME)
            cache.set_for_user(request.user, 'divisions', divisions, USER_SPACES_CACHE_TIME)
            cache.set_for_user(request.user, 'language_code_bidi', language_code, USER_SPACES_CACHE_TIME)

        request.META['MAUTHOR_USERNAME'] = request.user.username
        request.user.company = company
        if company is not None:
            request.META['MAUTHOR_COMPANY'] = company.title
        request.user.public_category = public_category
        request.user.divisions = divisions
        request.user.language_code_bidi = language_code_bidi

        return None

    def _read_company(self, request):
        divisions = {}
        company = get_company_for_user(request.user)
        public_category = None
        from settings import LANGUAGE_CODE
        language_code_bidi = LANGUAGE_CODE
        if company:
            cps = CorporatePublicSpace.objects.filter(company=company)
            try:
                language_code_bidi = CompanyProperties.objects.get(company=company).language_code or LANGUAGE_CODE
            except Exception:
                language_code_bidi = LANGUAGE_CODE
            if cps:
                public_category = cps[0].public_category
            for sa in request.user.spaceaccess_set.all():
                space = sa.space
                if space.is_corporate() and not space.is_top_level() and space.is_second_level():
                    divisions[space.id] = space
                elif space.is_corporate() and space.is_top_level():
                    for s in space.kids.all():
                        if s.is_corporate():
                            divisions[s.id] = s
                elif space.is_corporate() and not space.is_top_level() and not space.is_second_level():
                    if space.parent.is_second_level():
                        divisions[space.parent.id] = space.parent
        return company, public_category, divisions, language_code_bidi
