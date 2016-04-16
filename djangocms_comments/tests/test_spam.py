import os
from django.test import TestCase

from djangocms_comments.spam import Akismet
from .base import TestBase

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'
EVIL_USER_AGENT = 'Bot Evil/0.1'


class TestAkismet(TestBase, TestCase):
    def setUp(self):
        super(TestAkismet, self).setUp()
        try:
            akismet_api_key = os.environ['AKISMET_API_KEY']
        except KeyError:
            raise EnvironmentError('Provide AKISMET_API_KEY environment setting.')
        self.akismet = Akismet(akismet_api_key, is_test=True, blog_domain='http://127.0.0.1')

    def test_check_spam(self):
        self.assertTrue(self.akismet.check('viagra-test-123', 'viagra@spam-world.de', 'SPAM SPAM EGGS SPAMMM!!!1',
                                           '127.0.0.1', EVIL_USER_AGENT))

    def test_check_ham(self):
        self.assertFalse(self.akismet.check('Nekmo', 'contacto@nekmo.com', 'Great post! :D',
                                            '127.0.0.1', USER_AGENT))

    def test_report(self):
        self.akismet.report(True, 'Spammer', 'spammer@localhost', 'Great post! :D', '127.0.0.1', EVIL_USER_AGENT)
        self.akismet.report(False, 'Nekmo', 'contacto@nekmo.com', "No spam!", '127.0.0.1', USER_AGENT)
