'''
Created on 2011-03-19

@author: klangner
'''
from django import forms

class LabelForm(forms.Form):
    title = forms.CharField()
