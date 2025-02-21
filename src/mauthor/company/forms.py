from django import forms

class EditCompanyForm(forms.Form):
    space = forms.CharField(label="Name of the company to create")
    valid_until = forms.DateField(required=False, label="Valid until (eg. 2014-10-15)")
    max_accounts = forms.IntegerField(min_value=0, required=False)
