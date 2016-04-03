from django.conf.urls import *

from djangocms_comments.views import save_comment

urlpatterns = patterns('',
    # url(r'^$', 'main_view', name='app_main'),
    url(r'^ajax/$', save_comment, name='save_comment'),
)
