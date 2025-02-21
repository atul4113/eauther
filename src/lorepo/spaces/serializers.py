from lorepo.permission.models import Role
from lorepo.spaces.models import Space, UserSpacePermissions
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer


class SpaceSerializer (ModelSerializer):
    is_locked = SerializerMethodField()
    is_owner = SerializerMethodField()
    is_admin = SerializerMethodField()
    is_top_level = SerializerMethodField()
    publications = SerializerMethodField()
    roles = SerializerMethodField()

    class Meta:
        model = Space
        fields = ('id', 'title', 'is_locked', 'is_owner', 'is_admin', 'is_top_level', 'parent', 'contents_count', 'publications', 'roles')

    def get_is_locked(self, space):
        user = self.context.get('request').user
        # return is_company_locked(space.title)

        return False

    def get_is_owner(self, space):
        user = self.context.get('request').user
        usp = UserSpacePermissions.get_cached_usp_for_user(user)
        return user.is_superuser or usp.has_owner_role_for_space(space.id)

    def get_is_top_level(self, space):
        return space.is_top_level()

    def get_is_admin(self, space):
        user = self.context.get('request').user
        # TODO
        return False

    def get_publications(self, space):
        if self.context.get('publications') and space.is_project():
            spaces = space.kids.filter(is_deleted=False).order_by('title')
            return SpaceSerializer(spaces, many=True, context=self.context).data

        return []

    def get_roles(self, space):
        pass
        # get self.context.get('request').user space roles
        # return array of roles ids


class PublicationsInSpaceSerializer (ModelSerializer):
    publications = SerializerMethodField()

    class Meta:
        model = Space
        fields = ( 'id', 'title', 'parent', 'contents_count', 'publications')

    def get_publications(self, space):
        if self.context.get('publications') and space.is_project():
            spaces = space.kids.filter(is_deleted=False).order_by('title')
            return SpaceSerializer(spaces, many=True, context=self.context).data

        return []


class PermissionRoleSerializer(ModelSerializer):

    class Meta:
        model = Role
        fields = ('id', 'company', 'created_date', 'modified_date', 'name', 'permissions')
