from django.conf.urls import *

from djangocms_comments.views import save_comment

urlpatterns = patterns('',
    # url(r'^$', 'main_view', name='app_main'),
    url(r'^ajax/save_comment$', save_comment, name='djangocms_comments_save_comment'),
)
