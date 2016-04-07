from django.conf import settings

COMMENT_PUBLISHED_BY_DEFAULT = True
AKISMET_API_KEY = ''
MAX_LENGTH_COMMENT_BODY = 12000
COMMENT_TEXTAREA_ROWS = 4

# Override my settings usign Django Settings
for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
