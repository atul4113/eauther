from djangae.fields import ListField
from django.db import models
from lorepo.spaces.models import Space
import libraries.utility.cacheproxy as cache
from lorepo.spaces.signals import company_structure_has_changed

'''
    IMPORTANT NOTE:
    If you add new Permission, you have to run /user/trigger_task?path=/user/update_owners_permissions
    to update all Roles that have Owner permissions.
'''

class Permission():
    ASSET_BROWSE = 1
    ASSET_EDIT = 2
    ASSET_REMOVE = 3
    CONTENT_VIEW = 4
    CONTENT_REMOVE = 5
    CONTENT_EDIT_METADATA = 6
    CONTENT_MAKE_PUBLIC = 7
    CONTENT_COPY = 8
    CONTENT_EDIT = 9
    CONTENT_ICON = 10
    CONTENT_SHOW_HISTORY = 11
    CONTENT_EDIT_HISTORY = 12
    EXCHANGE_EXPORT = 13
    EXCHANGE_IMPORT = 14
    SPACE_ACCESS_MANAGE = 15
    SPACE_EDIT = 16
    SPACE_REMOVE = 17
    BACKUP_ADMIN = 18
    CORPORATE_UPLOAD_LOGO = 19
    CORPORATE_VIEW_DETAILS = 20
    CORPORATE_EDIT_DETAILS = 21
    CORPORATE_VIEW_PANEL = 22
    BUGTRACK_ADD = 23
    NARRATION_EXPORT = 24
    LOCALIZATION_CREATE = 25
    LOCALIZATION_LOCALIZE = 26
    LOCALIZATION_RESET = 27
    LOCALIZATION_EXPORT = 28
    LOCALIZATION_IMPORT = 29
    STATE_MANAGE = 30
    STATE_SET = 31
    COURSE_MANAGE = 32
    BULK_TEMPLATE_UPDATE = 33
    BULK_ASSETS_UPDATE = 34
    BUGTRACK_VIEW = 35

    def get_all(self):
        import inspect
        return [getattr(self, name) for name in dir(self) if not name.startswith('__') and not inspect.ismethod(getattr(self, name))]
    
    def get_more_actions_permissions(self):
        return [
                self.CONTENT_SHOW_HISTORY,
                self.CONTENT_EDIT,
                self.ASSET_BROWSE,
                self.EXCHANGE_EXPORT,
                self.NARRATION_EXPORT,
                self.LOCALIZATION_CREATE,
                self.LOCALIZATION_EXPORT,
                self.LOCALIZATION_RESET,
                self.ASSET_EDIT
                ]

PermissionTuples = {
    1  : ('Assets', 'Browse Assets'),
    2  : ('Assets', 'Upload/Edit Assets'),
    3  : ('Assets', 'Remove Assets'),
    4  : ('Content', 'View Lessons/Addons'),
    5  : ('Content', 'Remove Lessons/Addons'),
    6  : ('Content', 'Edit Metadata of Lessons/Addons'),
    7  : ('Content', 'Publish Lessons'),
    8  : ('Content', 'Copy Lessons'),
    9  : ('Content', 'Create/Edit Lessons/Addons'),
    10 : ('Content', 'Upload Lessons/Addons Icon'),
    11 : ('Content', 'Show Lessons History'),
    12 : ('Content', 'Set Lessons Current Version'),
    13 : ('Content', 'Export Lessons'),
    14 : ('Content', 'Import Lessons'),
    15 : ('Space', 'Manage Accesses To Projects/Publications'),
    16 : ('Space', 'Create/Edit Projects/Publications'),
    17 : ('Space', 'Remove Projects/Publications'),
    18 : ('Space', 'Create/Restore Projects Backup'),
    19 : ('Company', 'Upload Company Logo'),
    20 : ('Company', 'View Company Details'),
    21 : ('Company', 'Edit Company Details'),
    22 : ('Company', 'View Company Administration Panel'),
    23 : ('BugTrack', 'Report New Bugs In Bugtrack'),
    24 : ('Narration', 'Export Audio/Video Narrations'),
    25 : ('Localization', 'Create Lessons For Localization'),
    26 : ('Localization', 'Localize Lessons Prepared For Localization'),
    27 : ('Localization', 'Reset Localization Lessons To Original/Current Lesson'),
    28 : ('Localization', 'Export XLIFF'),
    29 : ('Localization', 'Import XLIFF'),
    30 : ('States', 'Manage Available State Sets'),
    31 : ('States', 'Select State Set For Publication'),
    32 : ('Course', 'Manage Courses'),
    33 : ('Space', 'Bulk Templates Update'),
    34 : ('Space', 'Bulk Assets Update'),
    35 : ('BugTrack', 'View Bugs'),
}


class Role(models.Model):
    name = models.CharField(max_length = 200)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    permissions = ListField(models.IntegerField())
    company = models.ForeignKey(Space, null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self).encode('utf-8')

    def __unicode__(self):
        return '%s' % self.name

    def get_permissions(self):
        from lorepo.permission.util import translate_perm_to_tuple
        return [translate_perm_to_tuple(perm) for perm in self.permissions]

    def save(self, *args, **kwargs):
        should_send = False
        if self.pk is not None:
            cache.set("role_%s" % self.pk, self)
            should_send = True

        super(Role, self).save(*args, **kwargs)
        if should_send:
            company_structure_has_changed.send(None, company_id=self.company_id)

    def delete(self, using=None):
        cache.delete("role_%s" % self.pk)
        return super(Role, self).delete(using=using)

    @staticmethod
    def get_cached_role(role_id):
        role = cache.get("role_%s" % role_id)
        if not role:
            role = Role.objects.get(pk=role_id)
            cache.set("role_%s" % role_id, role)
        return role

    @staticmethod
    def get_cached_roles(role_ids):
        roles = []
        for role_id in role_ids:
            roles.append(Role.get_cached_role(role_id))
        return roles