import django
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.db.models import TextField
from django.forms import ModelForm, ChoiceField
from django.template.defaultfilters import truncatechars
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

from djangocms_comments import settings
from djangocms_comments.models import AnonymousAuthor
from .models import CommentsConfig, Comment, MODERATED, REQUIRES_ATTENTION

EMPTY = (None, '---------')
MODERATED = [EMPTY] + MODERATED
REQUIRES_ATTENTION = [EMPTY] + REQUIRES_ATTENTION


if django.VERSION >= (1, 8):
    # Concat is not available in 1.7 and 1.6
    from django.db.models.functions import Concat


def get_user_agent(agent):
    try:
        from user_agents import parse
    except ImportError:
        return None
    return parse(agent)


class CommentsConfigAdmin(admin.ModelAdmin):
    pass

admin.site.register(CommentsConfig, CommentsConfigAdmin)


class StatusFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Comment status')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('published', _('Published')),
            ('hidden', _('Hidden (unpublished)')),
            ('spam', _('Spam')),
            ('edited', _('Edited by admin')),
            ('deleted', _('Deleted')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'published':
            return queryset.filter(moderated='', published=True)
        elif self.value() == 'hidden':
            return queryset.filter(published=False, moderated='')
        elif self.value() == 'spam':
            return queryset.filter(moderated='spam')
        elif self.value() == 'edited':
            return queryset.filter(moderated='edited')
        elif self.value() == 'deleted':
            return queryset.filter(moderated='deleted')


class ReadFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Revised comment')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'read'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            (True, _('Yes (read)')),
            (False, _('No (unread)')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'True':
            return queryset.filter(requires_attention='')
        elif self.value() == 'False':
            return queryset.exclude(requires_attention='')


class CommentAdminForm(ModelForm):
    moderated = ChoiceField(choices=MODERATED, required=False)
    requires_attention = ChoiceField(choices=REQUIRES_ATTENTION, required=False)

    class Meta:
        model = Comment
        exclude = ()


class CommentAdmin(admin.ModelAdmin):
    change_form_template = 'djangocms_comments/comment-admin-info.html'
    list_filter = (StatusFilter, ReadFilter)
    form = CommentAdminForm
    list_display = ('body_print', 'status', 'author_print', 'page_print', 'created_at_print')

    fieldsets = (
        (None, {
            'fields': ('published', 'body', 'moderated_reason')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (('moderated', 'requires_attention'), 'config', ('page_type', 'page_id'),
                       ('author_type', 'author_id')),
        }),
    )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        comment = self.get_object(request, unquote(object_id))
        if comment is not None:
            extra_context['user_agent'] = get_user_agent(comment.user_agent) or truncatechars(comment.user_agent, 60)
            comment.requires_attention = ''
            comment.save()
        return super(CommentAdmin, self).changeform_view(request, object_id=object_id, form_url=form_url,
                                                         extra_context=extra_context)

    def requires_attention_print(self, obj):
        pass
    requires_attention_print.short_description = _('Unread')

    def body_print(self, obj):
        return self._strong_unread(obj, truncatechars(obj.body, 80))
    body_print.short_description = _('Comment')

    def author_print(self, obj):
        return self._strong_unread(obj, obj.author)
    author_print.short_description = _('Author')
    author_print.admin_order_field = 'author_sort' if django.VERSION >= (1, 8) else None

    def page_print(self, obj):
        return self._strong_unread(obj, obj.page)
    page_print.short_description = _('Page')
    page_print.admin_order_field = 'page_sort' if django.VERSION >= (1, 8) else None

    def created_at_print(self, obj):
        return self._strong_unread(obj, timesince(obj.created_at))
    created_at_print.short_description = _('Created')
    created_at_print.admin_order_field = 'created_at'

    @staticmethod
    def _strong_unread(obj, output):
        if not obj.requires_attention:
            return output
        return mark_safe('<b>{}</b>'.format(escape(output)))

    def status(self, obj):
        status = obj.moderated
        if not status:
            status = 'published' if obj.published else 'hidden'
        return mark_safe('<span class="label label-{1}">{0}</span>'.format(
            status, {'spam': 'danger', 'edited': 'info',
                     'published': 'primary', 'deleted': 'warning'}.get(status, 'default')
        ))

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super(CommentAdmin, self).get_queryset(request)
        if django.VERSION >= (1, 8):
            # Concat is not available in 1.7 and 1.6
            qs = qs.annotate(author_sort=Concat('author_type', 'author_id', output_field=TextField()))
            qs = qs.annotate(page_sort=Concat('page_type', 'page_id', output_field=TextField()))
        return qs

    class Media:
        css = {
            'all': [
                'djangocms_comments/src/css/admin-{0}-bootstrap.css'.format('with' if settings.ADMIN_WITH_BOOTSTRAP
                                                                            else 'without'),
            ],
        }


admin.site.register(Comment, CommentAdmin)


class AnonymousAuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(AnonymousAuthor, AnonymousAuthorAdmin)
