from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from djangocms_comments import settings
from djangocms_comments.views import get_form_class, get_is_user
from .models import Comments, Comment


def get_object_from_context(context):
    return context.get('object') or context['current_page']


class CommentsPlugin(CMSPluginBase):
    model = Comments
    render_template = "djangocms_comments/comments.html"
    cache = False

    def render(self, context, instance, placeholder):
        obj = get_object_from_context(context)
        request = context['request']
        ct = ContentType.objects.get_for_model(obj)
        context['comments'] = self.get_comments(request, obj, ct)
        context['use_src'] = settings.COMMENTS_FORCE_STATIC_SRC
        context['comments_settings'] = settings
        initial = {
            'config_id': instance.config.pk,
            'page_type': ct.pk,
            'page_id': obj.pk,
        }
        context['form'] = get_form_class(request)(initial=initial)
        context['is_user'] = get_is_user(request)
        context['is_staff'] = request.user.is_staff
        return super(CommentsPlugin, self).render(context, instance, placeholder)

    @staticmethod
    def get_comments(request, obj, ct=None):
        ct = ct or ContentType.objects.get_for_model(obj)
        comments = Comment.objects.filter(page_type=ct, page_id=obj.pk)
        if not getattr(request.user, 'is_staff', False):
            comments = comments.filter(published=True).exclude(moderated='spam')
        return comments


plugin_pool.register_plugin(CommentsPlugin)
