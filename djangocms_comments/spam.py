import six

try:
    from django.utils.module_loading import import_string
except ImportError:
    from django.utils.module_loading import import_by_path as import_string

import djangocms_comments
from . import settings

_spam_cache = {}


class SpamProtection(object):
    def __init__(self, token=None, is_test=False, blog_domain=None):
        self.token = token
        self.is_test = is_test
        self.blog_domain = blog_domain

    def check(self, author, email, body, user_ip, user_agent, url=None, referrer='unknown', blog_domain=None):
        raise NotImplementedError

    def report(self, is_spam, author, email, body, user_ip, user_agent, url=None, referrer='unknown', blog_domain=None):
        raise NotImplementedError


class Akismet(SpamProtection):
    user_agent = 'djangocms-comments/{0}'.format(djangocms_comments.__version__)

    def __init__(self, token, is_test=False, blog_domain=None):
        super(Akismet, self).__init__(token, is_test, blog_domain)
        from akismet import Akismet as PyAkismet
        self.akismet = PyAkismet(token, application_user_agent=self.user_agent)

    def get_parameters(self, data):
        return dict(
            blog=self.blog_domain or data['blog_domain'],
            comment_author=data['author'],
            comment_author_email=data['email'],
            comment_author_url=data['url'],
            comment_content=data['body'],
            is_test=self.is_test,
            **dict((key, data[key]) for key in ['user_ip', 'user_agent', 'referrer']))

    def check(self, author, email, body, user_ip, user_agent, url=None, referrer='unknown', blog_domain=None):
        return self.akismet.check(**self.get_parameters(locals()))

    def report(self, is_spam, author, email, body, user_ip, user_agent, url=None, referrer='unknown', blog_domain=None):
        return self.akismet.submit(is_spam, **self.get_parameters(locals()))


class FakeSpamProtection(SpamProtection):
    def check(self, author, email, body, user_ip, user_agent, url=None, referrer='unknown', blog_domain=None):
        return False

    def report(self, is_spam, author, email, body, user_ip, user_agent, url=None, referrer='unknown', blog_domain=None):
        pass


def get_spam_protection(name='default'):
    if name not in _spam_cache:
        spam_protection = settings.SPAM_PROTECTION or {'default': {'BACKEND': FakeSpamProtection}}
        spam_protection = dict(spam_protection)
        conf = spam_protection[name]
        backend = conf.pop('BACKEND')
        conf = dict((key.lower(), value) for key, value in conf.items())
        module = import_string(backend) if isinstance(backend, six.string_types) else backend
        _spam_cache[name] = module(**conf)
    return _spam_cache[name]
