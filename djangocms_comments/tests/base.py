from cms.api import add_plugin
from cms.models import Placeholder
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory

from djangocms_comments.cms_plugins import CommentsPlugin
from djangocms_comments.models import Comment, CommentsConfig
from djangocms_comments.views import SaveComment
from djangocms_comments.widgets import SignedHiddenInput


class TestBase(object):
    factory = None
    staff_user = None
    normal_user = None
    config = None
    obj = None
    plugin_model_instance = None
    plugin_instance = None

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.anonymous = AnonymousUser()
        self.staff_user = get_user_model().objects.create_superuser(
            username='arthur', email='arthur@nekmo.com', password='grail')
        self.normal_user = get_user_model().objects.create_user(
            username='lancelot', email='lancelot@nekmo.com', password='grail')
        self.config = CommentsConfig.objects.create()
        self.obj = self.normal_user
        self.create_comment(self.obj, self.staff_user, published=True)
        self.create_comment(self.obj, self.normal_user, published=False)
        self.plugin_model_instance, self.plugin_instance = self.create_plugin()

    def create_comment(self, obj, author, published=True):
        Comment.objects.create(page=obj, author=author, body='This is a example comment!', user_ip='127.0.0.1',
                               user_agent='Django Test', published=published, config=self.config)

    def get_page_ct_id(self, obj=None):
        obj = obj or self.obj
        return dict(page_id=obj.pk, page_type=ContentType.objects.get_for_model(obj))

    def get_request(self, user, method='get', data=None, url='/demo', is_test=True, ip=None):
        data = data or {}  # Django 1.6 support
        request = getattr(self.factory, method)(url, data)
        request.user = user or self.anonymous
        request.is_test = is_test
        request.META['REMOTE_ADDR'] = ip or '127.0.0.1'
        return request

    def send_comment(self, author=None, body='', data=None, ajax=True, is_test=True, ip=None, obj=None):
        author = author or self.normal_user
        form = self.render_context_plugin(user=author, obj=obj)['form']
        new_data = {'body': body}
        new_data.update(self.get_sign_values(form))
        new_data.update(data or {})
        request = self.get_request(author, 'post', new_data, '/demo/{0}'.format('?ajax=1' if ajax else ''),
                                   is_test=is_test, ip=ip)
        response = SaveComment.as_view()(request)
        return response

    @staticmethod
    def get_sign_value(form, name):
        return form[name].field.widget.sign_value(name, form[name].value())

    def get_sign_values(self, form=None):
        form = form or self.render_context_plugin()['form']
        data = {}
        for name, bound in form.fields.items():
            if not isinstance(bound.widget, SignedHiddenInput):
                continue
            data[name] = self.get_sign_value(form, name)
        return data

    def render_context_plugin(self, obj=None, request=None, user=None):
        obj = obj or self.obj
        request = request or self.get_request(user or self.normal_user)
        return self.plugin_instance.render({'object': obj, 'request': request}, self.plugin_model_instance, None)

    def create_plugin(self):
        placeholder = Placeholder.objects.create(slot='test')
        model_instance = add_plugin(
            placeholder,
            CommentsPlugin,
            'en',
            config=self.config
        )
        plugin_instance = model_instance.get_plugin_class_instance()
        return model_instance, plugin_instance