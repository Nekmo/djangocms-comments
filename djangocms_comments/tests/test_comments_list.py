from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from djangocms_comments.cms_plugins import CommentsPlugin
from djangocms_comments.models import Comment
from .base import TestBase


class CommentsListFilter(TestBase, TestCase):

    def test_anonymous_only_published(self):
        request = self.factory.get('/demo')
        request.user = AnonymousUser()
        self.assertEquals(CommentsPlugin.get_comments(request, self.obj).count(), Comment.objects.filter(
            config=self.config, published=True, **self.get_page_ct_id()
        ).count())

    def test_normal_user_only_published(self, comments=None):
        request = self.factory.get('/demo')
        request.user = self.normal_user
        comments = comments or CommentsPlugin.get_comments(request, self.obj)
        self.assertEquals(comments.count(), Comment.objects.filter(
            config=self.config, published=True, **self.get_page_ct_id()
        ).count())

    def test_staff_all_comments(self):
        request = self.factory.get('/demo')
        request.user = self.staff_user
        self.assertEquals(CommentsPlugin.get_comments(request, self.obj).count(), Comment.objects.filter(
            config=self.config, **self.get_page_ct_id()
        ).count())

    def test_plugin_context(self):
        request = self.factory.get('/demo')
        request.user = self.normal_user
        context = self.plugin_instance.render({'object': self.obj, 'request': request}, self.plugin_model_instance,
                                              None)
        self.assertIn('comments', context)
        self.test_normal_user_only_published(context['comments'])
        self.assertIn('instance', context)
        self.assertEquals(context['instance'], self.plugin_model_instance)
