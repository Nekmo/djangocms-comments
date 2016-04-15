import django
from django.conf import settings

try:
    from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from cms.models.pluginmodel import CMSPlugin
from django.template.defaultfilters import truncatechars
from django.utils.translation import ugettext_lazy as _

MODERATED = [
    ('spam', _('Spam')),
    ('edited', _('Edited')),
    ('deleted', _('Deleted')),
]

REQUIRES_ATTENTION = [
    ('spam', _('Spam')),
    ('edited', _('Edited')),
    ('created', _('Created')),
]


class CommentsConfig(models.Model):
    name = models.CharField(max_length=32)
    open_comments = models.BooleanField(default=True)
    published_by_default = models.BooleanField(default=True)

    akismet = models.CharField(max_length=12, blank=True)

    def __str__(self):
        return self.name


class CommentsCMSPlugin(CMSPlugin):
    """AppHookConfig aware abstract CMSPlugin class for Aldryn Newsblog"""
    # avoid reverse relation name clashes by not adding a related_name
    # to the parent plugin

    config = models.ForeignKey(CommentsConfig)

    class Meta:
        abstract = True

    def copy_relations(self, old_instance):
        self.config = old_instance.config


class Comment(models.Model):
    config = models.ForeignKey(CommentsConfig)

    page_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+')
    page_id = models.PositiveIntegerField()
    page = GenericForeignKey('page_type', 'page_id')

    author_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='+')
    author_id = models.PositiveIntegerField()
    author = GenericForeignKey('author_type', 'author_id')

    body = models.TextField()

    requires_attention = models.CharField(blank='', max_length=16, choices=REQUIRES_ATTENTION)
    moderated = models.CharField(blank='', max_length=16, choices=MODERATED)
    moderated_reason = models.CharField(max_length=120, blank=True)
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    user_ip = models.GenericIPAddressField()
    # http://stackoverflow.com/questions/654921/how-big-can-a-user-agent-string-get
    user_agent = models.TextField()
    referrer = models.URLField(blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_edited(self):
        return self.updated_at.replace(second=0, microsecond=0) > self.created_at.replace(second=0, microsecond=0)

    def __str__(self):
        return u'[{}] {}'.format(self.page, truncatechars(self.body, 40))

    def __unicode__(self):
        return self.__str__()


class AnonymousAuthor(models.Model):
    username = models.CharField(max_length=32)
    email = models.EmailField()
    website = models.URLField(blank=True)
    comments = GenericRelation(Comment, object_id_field='author_id', content_type_field='author_type',
                               **{('related_name' if django.VERSION < (1, 7)
                                   else 'related_query_name'): 'anonymous_authors'})

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username


class Comments(CommentsCMSPlugin):
    published_by_default = models.BooleanField(default=True)
