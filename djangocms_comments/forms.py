import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, EmailField, URLField, IntegerField
from django.forms.widgets import Textarea
from django.utils.translation import ugettext_lazy as _

from djangocms_comments import settings
from djangocms_comments.models import AnonymousAuthor, CommentsConfig
from djangocms_comments.spam import get_spam_protection
from djangocms_comments.widgets import SignedHiddenInput
from .models import Comment


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_staff(request):
    return getattr(request.user, 'is_staff', False)


class CommentForm(ModelForm):
    signed_fields = ['config_id', 'page_id', 'page_type']
    config_id = IntegerField(widget=SignedHiddenInput)
    body = CharField(widget=Textarea(attrs={'rows': settings.COMMENT_TEXTAREA_ROWS}), label=_('Your comment'),
                     min_length=settings.MIN_LENGTH_COMMENT_BODY, max_length=settings.MAX_LENGTH_COMMENT_BODY)

    def __init__(self, data=None, **kwargs):
        self.request = kwargs.pop('request', None)
        # data = self.signer_fields(data, 'unsign')
        # kwargs['initial'] = self.signer_fields(kwargs.get('initial', {}))
        super(CommentForm, self).__init__(data, **kwargs)

    def security_validations(self):
        if Comment.objects.filter(user_ip=get_client_ip(self.request),
                                  created_at__gte=datetime.datetime.now() - datetime.timedelta(
                                      seconds=settings.COMMENT_WAIT_SECONDS)).count() \
                and settings.COMMENT_WAIT_SECONDS and not getattr(self.request, 'is_test', False):
            raise ValidationError(_('You must wait to post a new comment.'))

    def clean(self):
        cleaned_data = super(CommentForm, self).clean()
        if self.request and not is_staff(self.request):
            self.security_validations()
        return cleaned_data

    def clean_body(self):
        body = self.cleaned_data['body']
        if not is_staff(self.request):
            if settings.MAX_BREAKLINES_COMMENT_BODY and len(body.split('\n')) > settings.MAX_BREAKLINES_COMMENT_BODY:
                raise ValidationError(_('Your comment has too many line breaks.'))
            if settings.MAX_UPPERCASE_RATIO_COMMENT_BODY and sum(1 for c in body if c.isupper()) / (len(body) * 1.0) > \
                    settings.MAX_UPPERCASE_RATIO_COMMENT_BODY:
                raise ValidationError(_('Your comment has too many uppercase letters.'))
        return body

    def save(self, commit=True, author=None):
        author = author or self.request.user
        user_agent = self.request.META.get('HTTP_USER_AGENT', 'unknown')
        referrer = self.request.META.get('HTTP_REFERER', '')
        user_ip = get_client_ip(self.request)
        published = settings.COMMENT_PUBLISHED_BY_DEFAULT
        is_spam = False
        if is_staff(self.request):
            # Always published for admins
            published = True
        else:
            is_spam = get_spam_protection().check(author, author.email, self.cleaned_data['body'], user_ip, user_agent,
                                                  url=getattr(author, 'website', None), referrer='unknown',
                                                  blog_domain=self.request.get_host())
            published = published and not is_spam
        comment = Comment(author=author, user_ip=user_ip, user_agent=user_agent, referrer=referrer, published=published,
                          config=CommentsConfig.objects.get(pk=self.cleaned_data['config_id']),
                          **dict((key, self.cleaned_data[key]) for key in ['body', 'page_id', 'page_type']))
        if is_spam:
            comment.requires_attention = 'spam'
            comment.moderated = 'spam'
        elif not published:
            comment.requires_attention = 'created'
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

    def clean_username(self):
        username = self.cleaned_data['username']
        if settings.COMMENT_PREVENT_USURP_USERNAME and get_user_model().objects.filter(username=username).count():
            raise ValidationError(_('The chosen username belongs to a registered user.'))
        return username

    def save(self, commit=True, author=None):
        author, exists = AnonymousAuthor.objects.get_or_create(**dict((key, self.cleaned_data[key]) for key in
                                                                      ['username', 'email', 'website']))
        if not exists:
            author.save()
        return super(UnregisteredCommentForm, self).save(commit=commit, author=author)
