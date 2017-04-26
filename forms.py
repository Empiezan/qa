from django import forms

class SearchForm(forms.Form):
    keyword = forms.CharField(label='', max_length=100)

class LogForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget = forms.PasswordInput())

class LogoutForm(forms.Form):
    filler = forms.CharField(label='filler', max_length=100)

class AskForm(forms.Form):
    question = forms.CharField(label='', widget=forms.Textarea())

class DeleteForm(forms.Form):
    hidden = forms.CharField(widget = forms.HiddenInput())

class VoteForm(forms.Form):
    CHOICES = ("up","down")
    vote = forms.ChoiceField(choices = CHOICES)

class CommentForm(forms.Form):
    comment = forms.CharField(label='', widget=forms.Textarea(attrs={'rows': 3, 'cols': 40, 'style': 'height: 3em;'}))

class ReplyForm(forms.Form):
    reply = forms.CharField(label='', widget=forms.Textarea())

class ImageUploadForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()
