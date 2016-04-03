from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from djangocms_comments.forms import CommentForm
from .models import Comments


class CommentsPlugin(CMSPluginBase):
    model = Comments
    render_template = "djangocms_comments/comments.html"
    cache = False

    def render(self, context, instance, placeholder):
        obj = context['object']
        context['form'] = CommentForm()
        return super(CommentsPlugin, self).render(context, instance, placeholder)



plugin_pool.register_plugin(CommentsPlugin)
