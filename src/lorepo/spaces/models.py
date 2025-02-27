# -*- coding: utf-8 -*-
import bz2
import json

from djangae.fields import ListField
from django.contrib.auth.models import User
from django.db import models
import src.libraries.utility.cacheproxy as cache
from src.lorepo.spaces.signals import space_access_changed, company_structure_has_changed


class SpaceType():
    PRIVATE = 1
    PUBLIC = 2
    CORPORATE = 3


class Space(models.Model):
    title = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    left = models.IntegerField(default=0) # This is redundant, left here for tests
    right = models.IntegerField(default=0) # This is redundant, left here for tests
    parent = models.ForeignKey('self', null=True, blank=True, related_name="kids", on_delete=models.DO_NOTHING)
    top_level = models.ForeignKey('self', null=True, blank=True, related_name="subspaces", on_delete=models.DO_NOTHING)
    space_type = models.IntegerField(choices=[(SpaceType.PRIVATE, 'private'), (SpaceType.PUBLIC, 'public'), (SpaceType.CORPORATE, 'corporate')],default=1)
    rank = models.IntegerField(null=True, blank=True, default=100)
    is_deleted = models.BooleanField(default=False)
    contents_count = models.IntegerField(default=0)
    include_contents_in_editor = models.BooleanField(default=False)
    path = ListField(models.IntegerField()) # this is list of integers, not strings like in Content.spaces
    is_test = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return str(self).encode('utf-8')

    def __unicode__(self):
        return '%s' % (self.title)

    def __hash__(self):
        return self.pk

    def is_top_level(self):
        return self.parent == None

    def is_second_level(self):
        return len(self.path) == 2

    def is_private(self):
        return self.space_type == SpaceType.PRIVATE

    def is_public(self):
        return self.space_type == SpaceType.PUBLIC

    def is_corporate(self):
        return self.space_type == SpaceType.CORPORATE

    def save(self, *args, **kwargs):
        '''Stores new space.
        '''
        if self.pk is not None:
            super(Space, self).save(*args, **kwargs)
        elif self.parent is not None:
            if self.parent.top_level is not None:
                self.top_level = self.parent.top_level
            else:
                self.top_level = self.parent
            super(Space, self).save(*args, **kwargs)
        else:
            super(Space, self).save(*args, **kwargs) # Save the space to get it's id - needed for self ref
            self.top_level = self

    def is_project(self):
        if not self.parent or not self.top_level:
            return False
        return self.top_level.pk == self.parent.pk and self.is_corporate()

    def is_publication(self):
        if not self.parent or not self.top_level or not self.parent.parent:
            return False
        return self.top_level.pk == self.parent.parent.pk and self.is_corporate()

    def is_company(self):
        if not self.top_level:
            return False
        return self.top_level.pk == self.pk and self.is_corporate()

    def delete(self, using=None):
        super(Space, self).delete(using = using)
        if not self.is_public() and not self.is_top_level():
            company_structure_has_changed.send(None, company_id = self.top_level_id)

    @classmethod
    def get_cached(cls, space_id):
        space = cache.get("get_cached_space_%s" % (space_id))
        if not space:
            try:
                space = Space.objects.get(pk=space_id)
                cache.set("get_cached_space_%s" % (space_id), space)
            except Space.DoesNotExist:
                return None
        return space


class UserSpacePermissions(models.Model):
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now = True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    _deflated_content = models.BinaryField()

    def __init__(self, *args, **kwargs):
        self._inflated_content = None
        super(UserSpacePermissions, self).__init__(*args, **kwargs)

    @staticmethod
    def get_cached_usp_for_user(user):
        usp = cache.get("userspacepermissions_%s" % (user.id))
        if not usp:
            try:
                usp = UserSpacePermissions.objects.get(user = user)
                cache.set("userspacepermissions_%s" % (user.id), usp)
            except UserSpacePermissions.DoesNotExist:
                space_access_changed.send(None, user_id = user.id) #trigger creation of usp
                #return a dummy usp with no access rights
                usp = UserSpacePermissions()
                usp._inflated_content = {'stop_waitaminute':'fillmycup_putsomeliquerinit'}
        return usp

    @staticmethod
    def flush_usp_for_user(user):
        cache.delete("userspacepermissions_%s" % (user.id))

    def clear_permissions(self):
        self._inflated_content = None
        self._deflated_content = None

    def add_space_permissions(self, space_id, permissions):
        if not self._inflated_content:
            self._inflated_content = {}
        self._inflated_content[space_id] = permissions

    def get_permissions_for_space(self, space_id):
        if not self._inflated_content:
            #testing on a most problematic user at this time (~2,5k spaces), json is much faster than
            #cpickle and even repr->eval
            #the json.loads(bz2.decompress(self._deflated_content)) takes around 0.03s vs 0,18s for repr->eval
            self._inflated_content = json.loads(bz2.decompress(self._deflated_content))
        perm = None
        try:
            perm = self._inflated_content[space_id]
        except KeyError:
            try:
                perm = self._inflated_content[str(space_id)] #memcache screws with the dictionary datatypes
            except KeyError:
                perm = None
        return perm

    def has_owner_role_for_space(self, space_id):
        try:
            perms = set(self.get_permissions_for_space(space_id))
        except TypeError: #if get_permissions_for_space returns None
            return False
        from src.lorepo.permission.models import Permission
        all_perms = set(Permission().get_all())
        return perms == all_perms


    def delete(self, using=None):
        cache.delete("userspacepermissions_%s" % (self.user_id))
        return super(UserSpacePermissions, self).delete(using = using)

    def save(self, *args, **kwargs):
        cache.set("userspacepermissions_%s" % (self.user_id), self)
        self._deflated_content = bz2.compress(json.dumps(self._inflated_content))

        return super(UserSpacePermissions, self).save(*args, **kwargs)


class AccessRightType():
    READ = 1
    WRITE = 2
    OWNER = 3


class SpaceAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    space = models.ForeignKey(Space, on_delete=models.DO_NOTHING)

    # deprecated, use roles instead
    access_right = models.IntegerField(choices = [(AccessRightType.READ, 'read'), (AccessRightType.WRITE, 'write'), (AccessRightType.OWNER, 'owner')],
                                       default = AccessRightType.OWNER)
    is_deleted = models.BooleanField(default = False)
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now = True)

    roles = ListField(models.CharField())
    permissions = []

    def __init__(self, *args, **kwargs):
        if 'permissions' in kwargs:
            self.permissions = kwargs['permissions']
        else:
            self.permissions = []
        super(SpaceAccess, self).__init__(*args, **kwargs)

    def __str__(self):
        from src.lorepo.permission.models import Role
        return '%(username)s:%(title)s <%(roles)s>' % {
                 'title' : self.space.title,
                 'username' : self.user.username,
                 'roles' : ', '.join([Role.get_cached_role(role_id).name for role_id in self.roles])
                 }

    def readAccess(self):
        return self.access_right == 1

    def writeAccess(self):
        return self.access_right == 2

    def isOwner(self):
        from src.lorepo.permission.models import Role
        if not hasattr(self, 'roles'):
            return False
        return 'owner' in [Role.get_cached_role(role_id).name for role_id in self.roles] or self.user.is_superuser
    
    def hasAccess(self, perm):
        from src.lorepo.permission.models import Role
        if not hasattr(self, 'roles'):
            return False        
        return True in [perm in Role.get_cached_role(role_id).permissions for role_id in self.roles] or self.user.is_superuser

    def lock(self):
        the_copy = LockedSpaceAccess.objects.create(
            user = self.user,
            space = self.space,
            access_right = self.access_right,
            is_deleted = self.is_deleted,
            created_date = self.created_date,
            modified_date = self.modified_date,
            roles = self.roles
        )
        return the_copy

    def cache_permissions(self):
        from src.lorepo.permission.models import Role
        for role_id in self.roles:
            role = Role.get_cached_role(role_id)
            self.permissions.extend(role.permissions)
        self.permissions = set(self.permissions)

    def has_permission(self, permission):
        if len(self.permissions) == 0:
            self.cache_permissions()
        if isinstance(permission, str) or isinstance(permission, str):
            from src.lorepo.permission.models import Permission
            permission = getattr(Permission, permission)
        if permission in self.permissions:
            return True
        return False

    def delete(self, using=None):
        super(SpaceAccess, self).delete(using = using)
        cache.delete("space_access_%s_%s" % (self.space_id, self.user_id))
        space_access_changed.send(None, user_id = self.user_id, new_space_id = self.space_id, action = 'delete')

    def save(self, *args, **kwargs):
        super(SpaceAccess, self).save(*args, **kwargs)
        cache.set("space_access_%s_%s" % (self.space_id, self.user_id),self)
        space_access_changed.send(None, user_id = self.user_id, new_space_id = self.space_id, action = 'save')

class LockedSpaceAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    space = models.ForeignKey(Space, on_delete=models.DO_NOTHING)

    # deprecated, use roles instead
    access_right = models.IntegerField(choices = [(AccessRightType.READ, 'read'), (AccessRightType.WRITE, 'write'), (AccessRightType.OWNER, 'owner')],
                                       default = AccessRightType.OWNER)
    is_deleted = models.BooleanField(default = False)
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now = True)

    roles = ListField(models.CharField())

    def __str__(self):
        from src.lorepo.permission.models import Role
        return '%(username)s:%(title)s <%(roles)s>' % {
                 'title' : self.space.title,
                 'username' : self.user.username,
                 'roles' : ', '.join([Role.get_cached_role(role_id).name for role_id in self.roles])
                 }

    def unlock(self):
        the_copy = SpaceAccess(
            user = self.user,
            space = self.space,
            access_right = self.access_right,
            is_deleted = self.is_deleted,
            created_date = self.created_date,
            modified_date = self.modified_date,
            roles = self.roles
        )
        return the_copy