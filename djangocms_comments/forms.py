from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, EmailField, URLField, IntegerField
from django.forms.widgets import Textarea
from django.utils.translation import ugettext_lazy as _

from djangocms_comments import settings
from djangocms_comments.models import AnonymousAuthor, CommentsConfig
from djangocms_comments.widgets import SignedHiddenInput
from .models import Comment


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class CommentForm(ModelForm):
    signed_fields = ['config_id', 'page_id', 'page_type']
    config_id = IntegerField(widget=SignedHiddenInput)
    body = CharField(widget=Textarea(attrs={'rows': settings.COMMENT_TEXTAREA_ROWS}), label=_('Your comment'))

    def __init__(self, data=None, **kwargs):
        self.request = kwargs.pop('request', None)
        # data = self.signer_fields(data, 'unsign')
        # kwargs['initial'] = self.signer_fields(kwargs.get('initial', {}))
        super(CommentForm, self).__init__(data, **kwargs)

    def clean(self):
        cleaned_data = super(CommentForm, self).clean()
        if self.request and not getattr(self.request.user, 'is_staff', False):
            raise ValidationError(_('You must wait to post a new comment.'))
        return cleaned_data

    def save(self, commit=True, author=None):
        author = author or self.request.user
        published = settings.COMMENT_PUBLISHED_BY_DEFAULT
        if getattr(self.request.user, 'is_staff', False):
            # Always published for admins
            published = True
        comment = Comment(author=author, user_ip=get_client_ip(self.request),
                          config=CommentsConfig.objects.get(pk=self.cleaned_data['config_id']),
                          user_agent=self.request.META.get('HTTP_USER_AGENT', 'unknown'),
                          referrer=self.request.META.get('HTTP_REFERER', ''),
                          published=published,
                          **{key: self.cleaned_data[key] for key in ['body', 'page_id', 'page_type']})
        if commit:
            comment.save()
        return comment

    class Meta:
        widgets = {
            'page_id': SignedHiddenInput,
            'page_type': SignedHiddenInput,
        }
        model = Comment
        fields = ('body', 'page_type', 'page_id', 'config_id')


class UnregisteredCommentForm(CommentForm):
    username = CharField(max_length=32)
    email = EmailField()
    website = URLField(required=False)

    class Meta:
        widgets = {
            'page_id': SignedHiddenInput,
            'page_type': SignedHiddenInput,
        }
        model = Comment
        fields = ('username', 'email', 'website', 'body', 'page_type', 'page_id', 'config_id')

    def save(self, commit=True, author=None):
        author, exists = AnonymousAuthor.objects.get_or_create(**{key: self.cleaned_data[key] for key in
                                                                  ['username', 'email', 'website']})
        if not exists:
            author.save()
        return super(UnregisteredCommentForm, self).save(commit=commit, author=author)
