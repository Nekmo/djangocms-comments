from django.shortcuts import redirect

from djangocms_comments.forms import UnregisteredCommentForm, CommentForm


def save_comment(request):
    referrer = request.META.get('HTTP_REFERER', '')
    if request.user.is_anonymous():
        form = UnregisteredCommentForm(request.POST, request=request)
    else:
        form = CommentForm(request.POST, request=request)
    if form.is_valid():
        form.save()
    return redirect(referrer)
