from django import forms
from libraries.wiki.models import WikiPage, WikiPageTranslated
from django.core.exceptions import ValidationError
from libraries.wiki.util import make_url


class WikiPageForm(forms.Form):
    title = forms.CharField(error_messages={'required': 'Title is a required field'})
    text = forms.CharField(error_messages={'required': 'Text is a required field'})

    def clean_title(self):
        title = self.cleaned_data['title']
        url = make_url(title)
        pk = self.data['id']
        if pk == '':
            pk = 0
        else:
            pk = int(self.data['id'])

        if len(WikiPage.objects.filter(url=url)) > 0:
            for wp in WikiPage.objects.filter(url=url):
                if wp.id != pk:
                    raise ValidationError('Object with title ' + title + ' already exist')

        return self.cleaned_data['title']


class WikiPageTranslatedForm(forms.Form):
    title = forms.CharField(error_messages={'required': 'Title is a required field'})
    text = forms.CharField(error_messages={'required': 'Text is a required field'})

    def clean_title(self):
        title = self.cleaned_data['title']
        url = make_url(title)
        pk = self.data['id']
        if pk == '':
            pk = 0
        else:
            pk = int(self.data['id'])

        if len(WikiPageTranslated.objects.filter(url=url)) > 0:
            for wp in WikiPageTranslated.objects.filter(url=url):
                if wp.id == pk:
                    return self.cleaned_data['title']

        raise ValidationError('Object with title ' + title + ' already exist')


