from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from lorepo.spaces.models import Space, SpaceAccess
from lorepo.spaces.model.companyspacemap.company_space_map import CompanySpaceMap
from mauthor.utility.utils import sanitize_title


def chunks(sequence, n):
    for i in range(0, len(sequence), n):
        yield sequence[i:i + n]


class SpaceForm(forms.Form):
    title = forms.CharField()

    def clean_title(self):
        title = self.cleaned_data['title']

        return sanitize_title(title).strip(' ')


class RankForm(forms.Form):
    rank = forms.IntegerField(min_value=1, max_value=100)


# noinspection PyMethodMayBeStatic
class AccessForm(forms.Form):
    user = forms.CharField(error_messages={'required': 'Username is required'})
    space = forms.IntegerField(error_messages={'invalid': 'Choose the correct Project or Publication'})

    def __init__(self, *args, **kwargs):
        self.edit_mode = False
        self.company_id = None
        super(AccessForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(AccessForm, self).clean()
        username = cleaned_data.get('user')
        space_id = cleaned_data.get('space')

        if username and space_id:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise ValidationError('There is no user with username %(username)s' % locals())
            except User.MultipleObjectsReturned:
                raise ValidationError('There is some problem with username %(username)s. Please contact administration.' % locals())

            if not user.is_active:
                raise ValidationError('User has to be active.')

            have_space_access = SpaceAccess.objects.filter(user=user, space=space_id).count() > 0
            if have_space_access and not self.edit_mode:
                requested_space = Space.objects.get(pk=space_id)
                self._throw_validation_error('User {0} has already AccessRights to {1}', username, requested_space.title)

            self.check_branch_access(space_id, user)

        return cleaned_data

    def set_edit_mode(self, mode):
        self.edit_mode = mode
        
    def set_company_id(self, company_id):
        self.company_id = company_id
        
    def check_branch_access(self, space_id, user):
        company_space_map = CompanySpaceMap.cached(self.company_id)
        requested_space = Space.objects.get(pk=space_id)

        ids_to_check = []
        if requested_space.is_project():
            ids_to_check.append(requested_space.parent.id)
            project_tuple = company_space_map.space(requested_space.id)
            ids_to_check.extend(project_tuple["kids"])
        elif requested_space.is_publication():
            publication_tuple = company_space_map.space(requested_space.id)
            project_tuple = company_space_map.space(publication_tuple["parent_id"])
            
            ids_to_check.append(publication_tuple["parent_id"])
            ids_to_check.append(project_tuple["id"])
        else:
            self.check_company_branch(company_space_map, requested_space, user)

        for ids_chunk in chunks(ids_to_check, 30):
            if SpaceAccess.objects.filter(user=user, space__in=ids_chunk).count() > 0:
                self._throw_validation_error('User {0} has space access in parents or subspaces to space {1} and you can not change his access',
                                            user.username, requested_space.title)

    def check_company_branch(self, company_space_map, space, user):
        company = company_space_map.space(space.id)
        projects = company["kids"]

        for project_group in chunks(projects, 30):
            if SpaceAccess.objects.filter(user=user, space__in=project_group).count() > 0:
                self._throw_validation_error(
                    'User {0} has space access in parents or subspaces to space {1} and you can not change his access',
                    user.username, space.title)

        publications = []
        for project_group in chunks(projects, 30):
            for project in project_group:
                publications.extend(company_space_map.space(project)["kids"])

            for publications_chunk in chunks(publications, 30):
                if SpaceAccess.objects.filter(user=user, space__in=publications_chunk).count() > 0:
                    self._throw_validation_error(
                        'User {0} has space access in parents or subspaces to space {1} and you can not change his access',
                        user.username, space.title)

            publications = []

    def _get_unicode_text(self, text):

        if isinstance(text, str):
            return text
        else:
            return text.decode('utf-8')

    def _throw_validation_error(self, message, username, title):
        decoded_message = self._get_unicode_text(message)
        decoded_username = self._get_unicode_text(username)
        decoded_title = self._get_unicode_text(title)
        raise ValidationError(decoded_message.format(decoded_username, decoded_title))


class CorporateSpaceForm(forms.Form):
    user = forms.CharField(error_messages={'required': 'This field can\'t be null.'})
    space = forms.CharField(error_messages={'required': 'This field can\'t be null.'})

    def clean_user(self):
        username = self.cleaned_data['user']

        users = User.objects.filter(username=username)
        if len(users) != 1:
            raise ValidationError('Zero or more than one user found with username %(username)s' % locals())

        return username