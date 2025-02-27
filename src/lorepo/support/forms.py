from django import forms
from src.lorepo.support.models import TicketType
from src.lorepo.filestorage.forms import UploadForm

class TicketForm(forms.Form):
    title = forms.CharField(required=True)
    text = forms.CharField(required=True)
    lesson_url = forms.CharField(required=False)
    ticket_type = forms.ChoiceField(choices=[(TicketType.BUG, 'Bug'),
                                          (TicketType.QUESTION, 'Question'),
                                          (TicketType.REQUEST, 'Request'),
                                          ])

class CommentForm(forms.Form):
    text = forms.CharField(required=False)
