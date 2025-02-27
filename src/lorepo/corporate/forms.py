from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from src.lorepo.spaces.models import Space, SpaceType
from src.lorepo.spaces.util import get_top_level_owned_corporate_spaces, get_corporate_spaces_for_user


class CreateOwnerCompanyForm(forms.Form):
    space_id = forms.CharField(label="Company Id")
    user = forms.CharField(label="Username of the company owner")

    def clean_user(self):
        users = User.objects.filter(username=self.cleaned_data['user'])
        if len(users) != 0:
            user = users[0]
            spaces = get_corporate_spaces_for_user(user)
            if len(spaces):
                raise ValidationError('User already has a corporate space')
        else:
            raise ValidationError('User ' + self.cleaned_data['user'] + ' doesn\'t exist')
        return user

    def clean_space_id(self):
        spaces = Space.objects.filter(pk=self.cleaned_data['space_id'], space_type=SpaceType.CORPORATE, parent=None)
        if len(spaces) == 0:
            raise ValidationError('Space ' + self.cleaned_data['space_id'] + 'does not exists')
        return self.cleaned_data['space_id']

class CreateCompanyForm(forms.Form):
    space = forms.CharField(label="Name of the company to create")
    user = forms.CharField(label="Username of the company owner")
    valid_until = forms.DateField(required=False, label="Valid until (eg. 2014-10-15)")
    max_accounts = forms.IntegerField(min_value=0, required=False)

    def clean_user(self):
        users = User.objects.filter(username=self.cleaned_data['user'])
        if len(users) != 0:
            user = users[0]
            spaces = get_top_level_owned_corporate_spaces(user)
            if len(spaces):
                raise ValidationError('User already has corporate space')
        else:
            raise ValidationError('User ' + self.cleaned_data['user'] + ' doesn\'t exist')
        return user

    def clean_space(self):
        spaces = Space.objects.filter(title=self.cleaned_data['space'], space_type=SpaceType.CORPORATE, parent=None)
        if len(spaces) > 0:
            raise ValidationError('Space ' + self.cleaned_data['space'] + ' already exists')
        return self.cleaned_data['space']

class CopyToAccount(forms.Form):
    user = forms.CharField(label="Username")

    def clean_user(self):
        users = User.objects.filter(username=self.cleaned_data['user'])
        if len(users) != 0:
            user = users[0]
            return user
        else:
            raise ValidationError('User ' + self.cleaned_data['user'] + ' doesn\'t exist')
        return user
