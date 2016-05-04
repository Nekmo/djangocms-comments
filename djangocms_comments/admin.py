import django
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.db.models import TextField
from django.forms import ModelForm, ChoiceField, CharField, BooleanField
from django.forms.widgets import Input
from django.template.defaultfilters import truncatechars
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

from djangocms_comments import settings
from djangocms_comments.fields import SubmitButtonField, MultipleSubmitButtonRendered, MultipleSubmitButton, \
    ButtonGroupRenderer, Button
from djangocms_comments.models import AnonymousAuthor
from djangocms_comments.spam import get_spam_protection, FakeSpamProtection
from .models import CommentsConfig, Comment, MODERATED, REQUIRES_ATTENTION

EMPTY = (None, '---------')
MODERATED = [EMPTY] + MODERATED
REQUIRES_ATTENTION = [EMPTY] + REQUIRES_ATTENTION
CHANGE_TO_CHOICES = [
    ('hidden', _('Hidden')),
    ('published', _('Published')),
    ('spam', _('Spam')),
]

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
            return queryset.filter(published=False).exclude(moderated='spam')
        elif self.value() == 'spam':
            return queryset.filter(moderated='spam')
        elif self.value() == 'edited':
            return queryset.filter(moderated='edited', published=True)
        elif self.value() == 'deleted':
            return queryset.filter(moderated='deleted', published=True)


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
    # change_to = MultipleSubmitButtonRendered('change_to', 'published', {'enabled_classes': {
    #     'hidden': 'btn-primary', 'spam': 'btn-danger', 'published': 'btn-success'
    # }}, choices=CHANGE_TO_CHOICES)
    change_to = ChoiceField(widget=MultipleSubmitButton(attrs={'enabled_classes': {
        'hidden': 'btn-primary', 'spam': 'btn-danger', 'published': 'btn-success'
    }}), choices=CHANGE_TO_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        instance = kwargs['instance']
        kwargs['initial'] = kwargs.get('initial', {})
        if instance.moderated == 'spam':
            kwargs['initial']['change_to'] = 'spam'
        else:
            kwargs['initial']['change_to'] = 'published' if instance.published else 'hidden'
        super(CommentAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Comment
        exclude = ()


class CommentAdmin(admin.ModelAdmin):
    change_form_template = 'djangocms_comments/comment-admin-info.html'
    list_filter = (StatusFilter, ReadFilter)
    form = CommentAdminForm
    list_display = ('body_print', 'status', 'author_print', 'page_print', 'created_at_print')
    _user_message = None

    fieldsets = (
        (None, {
            'fields': ('body', 'moderated_reason')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (('moderated', 'requires_attention'), 'config', ('page_type', 'page_id'),
                       ('author_type', 'author_id')),
        }),
    )

    def get_actions(self, request):
        actions = super(CommentAdmin, self).get_actions(request)
        for action in ['make_spam', 'make_published', 'make_soft_deleted', 'make_hidden']:
            actions[action] = (getattr(self, action), action, getattr(getattr(self, action), 'verbose_name', action))
        return actions

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        comment = self.get_object(request, unquote(object_id))
        if comment is not None:
            extra_context['user_agent'] = get_user_agent(comment.user_agent) or truncatechars(comment.user_agent, 60)
            comment.requires_attention = ''
            comment.save()
        changeform = super(CommentAdmin, self).changeform_view(request, object_id=object_id, form_url=form_url,
                                                               extra_context=extra_context)
        return changeform

    def save_model(self, request, obj, form, change):
        if obj.pk and form.cleaned_data['body'] != self.model.objects.get(pk=obj.pk).body:
            self.message_user(request, _('The comment has been marked as edited.'))
            obj.moderated_by = request.user
            obj.moderated = 'edited'
        if form.cleaned_data['change_to']:
            obj.moderated_by = request.user
            change_to = form.cleaned_data['change_to']
            if change_to == 'spam':
                obj.moderated = ''
                get_spam_protection().report(True, obj.author, obj.author.email, obj.body, obj.user_ip,
                                             obj.user_agent, url=getattr(obj.author, 'website', None),
                                             referrer=obj.referrer, blog_domain=request.get_host())
                obj.moderated = 'spam'
            obj.published = change_to == 'published'
            msg = {
                'spam': _('The comment has been marked as spam and is no longer visible.'),
                'hidden': _('The comment has been marked as hidden and is no longer visible.'),
                'published': _('The comment has been marked as published.'),
            }[change_to]
            if change_to == 'spam' and get_spam_protection() is not FakeSpamProtection:
                msg += _(' It has also been reported as spam to {0}.').format(get_spam_protection().__class__.__name__)
            self.message_user(request, msg)
        if request.POST.get('toggle_soft_delete'):
            obj.moderated_by = request.user
            obj.moderated = '' if obj.moderated == 'deleted' else 'deleted'
            msg = _('The comment has been moderate and displayed as deleted.') if obj.moderated == 'deleted' \
                else _('The comment has been restored.')
            self.message_user(request, msg)
        return super(CommentAdmin, self).save_model(request, obj, form, change)

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
        if not obj.published and status != 'spam':
            status = 'hidden'
        elif not status and obj.published:
            status = 'published'
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

    def _make_base(self, request, queryset, action, message):
        queryset = queryset.exclude(moderated='spam')
        for comment in queryset.all():
            action(comment)
            comment.save()
        message_bit = _("1 comment was") if queryset.count() == 1 else _("{} comment were").format(queryset.count())
        self.message_user(request, "%s successfully reported and marked as spam." % message_bit)

    def make_spam(self, request, queryset):
        def action(comment):
            comment.moderated = 'spam'
        self._make_base(request, queryset.exclude(moderated='spam'), action,
                        _("%s successfully reported and marked as spam."))
    make_spam.verbose_name = _('Mark and report spam')

    def make_soft_deleted(self, request, queryset):
        def action(comment):
            comment.moderated = 'deleted'
            comment.published = True
        self._make_base(request, queryset.exclude(moderated='deleted', published=True), action,
                        _("%s successfully removed usign soft delete."))
    make_soft_deleted.verbose_name = _('Remove usign soft delete')

    def make_published(self, request, queryset):
        def action(comment):
            comment.moderated = ''
            comment.published = True
        self._make_base(request, queryset.exclude(moderated='', published=True), action,
                        _("%s successfully published."))
    make_published.verbose_name = _('Publish')

    def make_hidden(self, request, queryset):
        def action(comment):
            comment.published = False
        self._make_base(request, queryset.exclude(published=False), action,
                        _("%s successfully hidden."))
    make_hidden.verbose_name = _('Hide')

    class Media:
        css = {
            'all': [
                'djangocms_comments/{0}/css/admin-{1}-bootstrap.css'.format(
                    'src' if settings.COMMENTS_FORCE_STATIC_SRC else 'dist',
                    'with' if settings.COMMENTS_ADMIN_WITH_BOOTSTRAP3 else 'without'),
            ],
        }


admin.site.register(Comment, CommentAdmin)


class AnonymousAuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(AnonymousAuthor, AnonymousAuthorAdmin)
