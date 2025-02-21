from captcha.fields import ReCaptchaField
from math_captcha import MathCaptchaForm
from django import forms
from country_utils.countries import COUNTRY_CHOICES

USERS_CHOICES = (
    ('', 'Select number of users'),
    ('1', '1'),
    ('3', '3'),
    ('5', '5'),
    ('10', '10'),
    ('20', '20'),
    ('40', '40')
)

PLAN_CHOICES = (
    ('', 'Select plan'),
    ('monthly', 'monthly'),
    ('yearly', 'yearly'),
    ('3 years', '3 years')
)


class SupportForm(MathCaptchaForm):
    name = forms.CharField()
    company = forms.CharField()
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    
class ContactForm(SupportForm):
    l = sorted(COUNTRY_CHOICES, key=lambda e: e[1])
    l.insert(0, ('', '-- Select country --'))
    country = forms.ChoiceField(l)


class OrderForm(forms.Form):
    name = forms.CharField()
    company = forms.CharField()
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea, required=False)
    l = sorted(COUNTRY_CHOICES, key=lambda e: e[1])
    l.insert(0, ('', 'Select country'))
    country = forms.ChoiceField(l)
    u = USERS_CHOICES
    users = forms.ChoiceField(u, required=True)
    price = forms.CharField(required=False)
    captcha = ReCaptchaField()

    def set_users (self, users):
        self.fields['users'].initial = users
