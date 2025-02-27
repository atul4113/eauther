from src.libraries.utility.noseplugins import FormattedOutputTestCase
from django.contrib.auth.models import User
from src.lorepo.spaces.models import Space
from src.lorepo.permission.util import verify_space_access, check_space_access,\
    verify_content_access
from src.lorepo.permission.models import Permission
from django.core.exceptions import PermissionDenied
from src.lorepo.mycontent.models import Content

class UtilityTests(FormattedOutputTestCase):
    fixtures = ['permission_views.json']

    def test_verify_has_access(self):
        space = Space.objects.get(pk=58)
        user = User.objects.get(pk=8)
        self.assertTrue(verify_space_access(space, user, Permission.CONTENT_VIEW))

    def test_verify_has_no_access(self):
        space = Space.objects.get(pk=59)
        user = User.objects.get(pk=8)
        self.assertFalse(verify_space_access(space, user, Permission.CONTENT_EDIT))

    def test_check_space_access(self):
        space = Space.objects.get(pk=58)
        user = User.objects.get(pk=8)
        self.assertTrue(check_space_access(space, user, Permission.CONTENT_VIEW))

    def test_has_no_spaceaccess(self):
        space = Space.objects.get(pk=59)
        user = User.objects.get(pk=8)
        self.assertRaises(PermissionDenied, check_space_access, space, user, Permission.CONTENT_EDIT)

    def test_verify_content_access(self):
        user = User.objects.get(pk=74)
        content = Content.objects.get(pk=64)
        self.assertTrue(verify_content_access(content, user, Permission.CONTENT_EDIT))