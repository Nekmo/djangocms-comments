from django.shortcuts import redirect

from djangocms_comments.forms import UnregisteredCommentForm


def save_comment(request):
    referrer = request.META['HTTP_REFERER']
    form = UnregisteredCommentForm(request.POST, request=request)
    if form.is_valid():
        form.save()
    return redirect(referrer)
