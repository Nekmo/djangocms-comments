from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from djangocms_comments.forms import UnregisteredCommentForm, CommentForm
from .models import Comments, Comment


class CommentsPlugin(CMSPluginBase):
    model = Comments
    render_template = "djangocms_comments/comments.html"
    cache = False

    def render(self, context, instance, placeholder):
        obj = context['object']
        request = context['request']
        ct = ContentType.objects.get_for_model(obj)
        comments = Comment.objects.filter(page_type=ct, page_id=obj.pk)
        if not getattr(request.user, 'is_staff', False):
            comments = comments.filter(published=True)
        context['comments'] = comments
        initial = {
            'config_id': instance.config.pk,
            'page_type': ct.pk,
            'page_id': obj.pk,
        }
        if request.user.is_anonymous():
            context['form'] = UnregisteredCommentForm(initial=initial)
            context['is_user'] = False
        else:
            context['form'] = CommentForm(initial=initial)
            context['is_user'] = True
        return super(CommentsPlugin, self).render(context, instance, placeholder)


plugin_pool.register_plugin(CommentsPlugin)
