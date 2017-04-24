from django import forms

from qa.models import Post

class LogForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget = forms.PasswordInput())

class LogoutForm(forms.Form):
    filler = forms.CharField(label='filler', max_length=100)

class AskForm(forms.Form):
    question = forms.CharField(label='', widget=forms.Textarea())

class DeleteForm(forms.Form):
    hidden = forms.CharField(widget = forms.HiddenInput())
