from django.conf.urls import *

from djangocms_comments.views import SaveComment

urlpatterns = [
    url(r'^ajax/save_comment$', SaveComment.as_view(), name='djangocms_comments_save_comment'),
]
