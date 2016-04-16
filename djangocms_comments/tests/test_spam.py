import os
from django.test import TestCase

from djangocms_comments.spam import Akismet
from .base import TestBase


class TestSpam(TestBase, TestCase):
    def setUp(self):
        super(TestSpam, self).setUp()
        try:
            akismet_api_key = os.environ['AKISMET_API_KEY']
        except KeyError:
            raise EnvironmentError('Provide AKISMET_API_KEY environment setting.')
        self.akismet = Akismet(akismet_api_key, is_test=True, blog_domain='http://127.0.0.1')

    def test_akismet_check_spam(self):
        self.assertTrue(self.akismet.check('viagra-test-123', 'viagra@spam-world.de', 'SPAM SPAM EGGS SPAMMM!!!1',
                                           '127.0.0.1', 'Bot Evil/0.1'))
