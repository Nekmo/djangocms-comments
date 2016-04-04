from django.forms import ModelForm, CharField, EmailField, URLField, IntegerField
from django.forms.widgets import HiddenInput, Textarea
from django.utils.translation import ugettext_lazy as _

from djangocms_comments.models import AnonymousAuthor, CommentsConfig
from .models import Comment


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class CommentForm(ModelForm):
    config_id = IntegerField(widget=HiddenInput)
    body = CharField(widget=Textarea(attrs={'rows': '4'}), label=_('Your comment'))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CommentForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, author=None):
        author = author or self.request.user
        comment = Comment(author=author, user_ip=get_client_ip(self.request),
                          config=CommentsConfig.objects.get(pk=self.cleaned_data['config_id']),
                          user_agent=self.request.META.get('HTTP_USER_AGENT', 'unknown'),
                          referrer=self.request.META.get('HTTP_REFERER', ''),
                          **{key: self.cleaned_data[key] for key in ['body', 'page_id', 'page_type']})
        if commit:
            comment.save()
        return commit

    class Meta:
        widgets = {
            'page_id': HiddenInput,
            'page_type': HiddenInput,
        }
        model = Comment
        fields = ('body', 'page_type', 'page_id', 'config_id')


class UnregisteredCommentForm(CommentForm):
    username = CharField(max_length=32)
    email = EmailField()
    website = URLField(required=False)

    class Meta:
        widgets = {
            'page_id': HiddenInput,
            'page_type': HiddenInput,
        }
        model = Comment
        fields = ('username', 'email', 'website', 'body', 'page_type', 'page_id', 'config_id')

    def save(self, commit=True, author=None):
        author, exists = AnonymousAuthor.objects.get_or_create(**{key: self.cleaned_data[key] for key in
                                                                  ['username', 'email', 'website']})
        if not exists:
            author.save()
        return super(UnregisteredCommentForm, self).save(commit=commit, author=author)