from django import forms

class AddSetForm(forms.Form):
    name = forms.CharField(max_length=200)

class AddStateForm(forms.Form):
    name = forms.CharField(max_length=200)
    set_id = forms.IntegerField()
    percentage = forms.IntegerField(initial=0, min_value=0, max_value=100)

class RenameStateForm(forms.Form):
    name = forms.CharField(max_length=200)
    state_id = forms.IntegerField()
