from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.forms import ModelForm, ChoiceField
from django.template.defaultfilters import truncatechars
from django.utils.translation import ugettext_lazy as _

from djangocms_comments.models import AnonymousAuthor
from .models import CommentsConfig, Comment, MODERATED, REQUIRES_ATTENTION

EMPTY = (None, '---------')
MODERATED = [EMPTY] + MODERATED
REQUIRES_ATTENTION = [EMPTY] + REQUIRES_ATTENTION


def get_user_agent(agent):
    try:
        from user_agents import parse
    except ImportError:
        return None
    return parse(agent)


class CommentsConfigAdmin(admin.ModelAdmin):
    pass

admin.site.register(CommentsConfig, CommentsConfigAdmin)


class CommentAdminForm(ModelForm):
    moderated = ChoiceField(choices=MODERATED, required=False)
    requires_attention = ChoiceField(choices=REQUIRES_ATTENTION, required=False)

    class Meta:
        model = Comment
        exclude = ()


class CommentAdmin(admin.ModelAdmin):
    change_form_template = 'djangocms_comments/comment-admin-info.html'
    form = CommentAdminForm

    fieldsets = (
        (None, {
            'fields': ('published', 'body', 'moderated', 'moderated_reason', 'requires_attention')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('config', ('page_type', 'page_id'), ('author_type', 'author_id')),
        }),
    )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        comment = self.get_object(request, unquote(object_id))
        if comment is not None:
            extra_context['user_agent'] = get_user_agent(comment.user_agent) or truncatechars(comment.user_agent, 60)
        return super(CommentAdmin, self).changeform_view(request, object_id=object_id, form_url=form_url,
                                                         extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    class Media:
        css = {
            'all': ['djangocms_comments/css/comment-admin.css'],
        }


admin.site.register(Comment, CommentAdmin)


class AnonymousAuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(AnonymousAuthor, AnonymousAuthorAdmin)
