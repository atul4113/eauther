from django import forms

class AddBugForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(required=False)