from django.forms import ModelForm, CharField, EmailField, URLField
from django.forms.widgets import HiddenInput

from .models import Comment


class CommentForm(ModelForm):
    username = CharField(max_length=32)
    email = EmailField()
    website = URLField(required=False)

    class Meta:
        widgets = {
            'page_id': HiddenInput,
            'page_type': HiddenInput,
        }
        model = Comment
        fields = ('username', 'email', 'website', 'body', 'page_type', 'page_id')
