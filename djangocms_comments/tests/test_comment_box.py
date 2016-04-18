import math

import cms
import django
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import SuspiciousOperation
from django.test import TestCase

from djangocms_comments import settings
from djangocms_comments.forms import UnregisteredCommentForm
from djangocms_comments.models import Comment
from djangocms_comments.views import SaveComment
from .base import TestBase

PATSY_BODY = """Sir Lancelot: Look, my liege!
King Arthur: [awed] Camelot!
Sir Galahad: Camelot!
Sir Lancelot: Camelot!
"Patsy: It's only a model."""


class CommentsListFilter(TestBase, TestCase):
    def test_context_has_form(self):
        self.assertIn('form', self.render_context_plugin())

    def test_plugin_comment_form(self):
        form = self.render_context_plugin(user=self.anonymous)['form']
        self.assertIsInstance(form, UnregisteredCommentForm)
        self.assertIn('config_id', form.initial)
        self.assertEqual(form.initial['config_id'], self.config.pk)
        self.assertIn('page_type', form.initial)
        self.assertEqual(form.initial['page_type'], ContentType.objects.get_for_model(self.obj).pk)
        self.assertIn('page_id', form.initial)
        self.assertEqual(form.initial['page_id'], self.obj.pk)

    def test_anonymous_comment(self):
        data = {
            'username': 'Patsy', 'email': 'squire@camelot.com', 'website': 'http://camelot.com/test_anonymous_comment',
            'body': PATSY_BODY + ' test_anonymous_comment',
        }
        response = self.send_comment(self.anonymous, data=data)
        self.assertFalse(response.context_data['form'].errors)
        self.assertFalse(response.context_data['form'].is_bound)
        q = dict(config=self.config, **self.get_page_ct_id())
        if django.VERSION < (1, 7):
            q['body'] = data['body']
        else:
            q['anonymous_authors__website'] = data['website']
        self.assertEqual(Comment.objects.filter(**q).count(), 1)

    def test_user_comment(self):
        body = 'CommentsListFilter.test_user_comment test.' + ('This is a test!' * 8)
        response = self.send_comment(self.normal_user, body)
        self.assertFalse(response.context_data['form'].errors)
        self.assertFalse(response.context_data['form'].is_bound)
        try:
            Comment.objects.get(config=self.config, body=body, **self.get_page_ct_id())
        except Comment.DoesNotExist:
            self.fail('The comment has not been created')

    def test_body_len_validation(self):
        # Min
        body = 'spam eggs '
        body = (body * (len(body) // settings.MIN_LENGTH_COMMENT_BODY))[:-1]
        response = self.send_comment(body=body)
        self.assertEqual(len(response.context_data['form'].errors), 1)
        # Max
        body = 'NOBODY expects the Spanish Inquisition! '
        body = (body * (len(body) // settings.MAX_LENGTH_COMMENT_BODY)) + '!'
        response = self.send_comment(body=body)
        self.assertEqual(len(response.context_data['form'].errors), 1)

    def test_max_uppercase_ratio_comment_body(self):
        ratio = settings.MAX_UPPERCASE_RATIO_COMMENT_BODY
        body = 'spam eggs ' * 100
        body = body[:int(math.ceil(len(body) * ratio) + 1)].upper() + body[int(math.ceil(len(body) + 1 * ratio)):]
        response = self.send_comment(body=body)
        self.assertEqual(len(response.context_data['form'].errors), 1)

    def test_max_breaklines_comment_body(self):
        ratio = settings.MAX_BREAKLINES_COMMENT_BODY
        body = '\n'.join(['spam'] * (ratio + 1))
        response = self.send_comment(body=body)
        self.assertEqual(len(response.context_data['form'].errors), 1)

    def test_anonymous_form_error(self):
        body = 'test_anonymous_form_error ' * 100
        response = self.send_comment(self.anonymous, body=body)
        self.assertEqual(len(response.context_data['form'].errors), 2)  # Username, email
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(config=self.config, body=body,**self.get_page_ct_id())

    def test_user_form_error(self):
        body = ''  # Empty comment is not allowed
        response = self.send_comment(self.normal_user, body=body)
        self.assertEqual(len(response.context_data['form'].errors), 1)  # Comment is required
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(config=self.config, body=body, **self.get_page_ct_id())

    def test_sign_validation(self):
        signed_values = self.get_sign_values(self.render_context_plugin()['form'])
        for field_name in ['page_id', 'page_type', 'config_id']:
            with self.assertRaises(SuspiciousOperation):
                self.send_comment(data={field_name: signed_values[field_name].split(':')[0]})
            with self.assertRaises(SuspiciousOperation):
                self.send_comment(data={field_name: signed_values[field_name] + '0'})
        with self.assertRaises(SuspiciousOperation):
            self.send_comment(data={'page_id': signed_values['config_id'].split(':')[0]})

    def test_comment_wait_seconds(self):
        author = self.normal_user
        ip = '192.168.1.1'
        self.send_comment(author, ip=ip, is_test=False,
                          body="Listen. Strange women lying in ponds distributing swords is no basis "
                               "for a system of government. Supreme executive power derives from a "
                               "mandate from the masses, not from some farcical aquatic ceremony.")
        new_data = {'body': "You can't expect to wield supreme power just"
                            "'cause some watery tart threw a sword at you! " * 4}
        new_data.update(self.get_sign_values())
        request = self.get_request(author, 'post', new_data, '/demo/?ajax=1', is_test=False, ip=ip)
        response = SaveComment.as_view()(request)
        self.assertEqual(len(response.context_data['form'].errors), 1)

    def test_comment_in_page(self):
        body = 'CommentsListFilter.test_comment_in_page test.' + ('This is a test!' * 8)
        page = cms.api.create_page('Test', 'fullwidth.html', 'en')
        response = self.send_comment(self.normal_user, body, obj=page)
        self.assertEqual(len(response.context_data['form'].errors), 0)
        try:
            Comment.objects.get(config=self.config, body=body)
        except Comment.DoesNotExist:
            self.fail('The comment has not been created')
