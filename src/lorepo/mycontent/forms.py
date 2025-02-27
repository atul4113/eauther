from django import forms
import re
import unidecode
from django.core.exceptions import ValidationError
from src.lorepo.mycontent.models import Content, ContentType

class ContentMetadataForm(forms.Form):
    title = forms.CharField()
    tags = forms.CharField(required=False)
    description = forms.CharField(required=False)
    short_description = forms.CharField(required=False)
    space_id = forms.Select()
    public_space_id = forms.Select()
    is_template = forms.CheckboxInput()
    passing_score = forms.IntegerField(min_value=0, max_value=100, initial=0, required=False)
    score_type = forms.ChoiceField(choices=[('first', 'first'), ('last', 'last')], required=False)

    def initialize(self, content):
        self.data['description'] = content.description
        self.data['short_description'] = content.short_description
        self.data['title'] = content.title
        self.data['tags'] = content.tags
        self.data['is_template'] = content.content_type == ContentType.TEMPLATE
        self.data['passing_score'] = content.passing_score
        self.data['score_type'] = content.get_score_type()

class AddAddonForm(ContentMetadataForm):
    name = forms.CharField(required=False)

    def clean_name(self):
        name = self.cleaned_data['name']
        name = re.sub(' ', '_', name)

        name = unidecode.unidecode(name)
        name = re.sub('[^0-9a-zA-Z_]', '', name)

        if not re.search('[A-Za-z]+[0-9A-Za-z]+', name):
            raise ValidationError('Name should contain at least one letter or digit and start with a letter')

        contents = Content.objects.filter(name=name)
        if len(contents) > 0:
            raise ValidationError('Content with name %(name)s already exists in database. Please choose different name' % { 'name' : name })

        return name

class AddonMetadataForm(ContentMetadataForm):
    example_id = forms.IntegerField(required=False)
    category_id = forms.IntegerField(required=False)
    
class DefaultTemplateForm(forms.Form):
    template_id = forms.CharField()
    
    def clean_template_id(self):
        if not re.search('^[\d]+$', self.cleaned_data['template_id']):
            raise ValidationError('Template id must be a number !')
        return self.cleaned_data['template_id']
