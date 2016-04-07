from django.conf.urls import *

from djangocms_comments.views import SaveComment

urlpatterns = patterns('',
    # url(r'^$', 'main_view', name='app_main'),
    url(r'^ajax/save_comment$', SaveComment.as_view(), name='djangocms_comments_save_comment'),
)
