from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import FormView

from djangocms_comments.forms import UnregisteredCommentForm, CommentForm


class SaveComment(FormView):
    comment = None
    template_name = 'djangocms_comments/comment_box.html'

    def get_form_class(self):
        if self.request.user.is_anonymous():
            return UnregisteredCommentForm
        else:
            return CommentForm

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = form_class(self.request.POST, request=self.request)
        return form

    def form_valid(self, form):
        self.comment = form.save()
        return form

    def form_invalid(self, form):
        return form

    def post(self, request, *args, **kwargs):
        form = super(SaveComment, self).post(request, *args, **kwargs)
        if request.GET.get('ajax'):
            return self.render_to_response({
                'form': form,
                'comment': self.comment,
                'is_user': not request.user.is_anonymous()
            })
        referrer = request.META.get('HTTP_REFERER', '')
        return redirect(referrer)
