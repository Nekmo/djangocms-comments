from django.conf.urls import *

from djangocms_comments.views import SaveComment
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    url(r'^ajax/save_comment$', SaveComment.as_view(), name='djangocms_comments_save_comment'),
]

# ('',
#     # url(r'^$', 'main_view', name='app_main'),
#     url(r'^ajax/save_comment$', SaveComment.as_view(), name='djangocms_comments_save_comment'),
# )
