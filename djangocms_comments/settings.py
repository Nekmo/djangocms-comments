from django.conf import settings

COMMENT_PUBLISHED_BY_DEFAULT = True
SPAM_PROTECTION = {}  # {'default': {'BACKEND': 'djangocms_comments.spam.Akismet', 'TOKEN': '...'}}
MIN_LENGTH_COMMENT_BODY = 50
MAX_LENGTH_COMMENT_BODY = 12000
MAX_BREAKLINES_COMMENT_BODY = 12
MAX_UPPERCASE_RATIO_COMMENT_BODY = 0.3
COMMENT_TEXTAREA_ROWS = 4
COMMENT_WAIT_SECONDS = 120
COMMENT_PREVENT_USURP_USERNAME = True
COMMENTS_ADMIN_WITH_BOOTSTRAP3 = True
COMMENTS_FORCE_STATIC_SRC = False

BOOTSTRAP3_COLS = 24
BOOTSTRAP3_AVATAR_COLS = 3
BOOTSTRAP3_SELF_ANON_AVATAR_COLS = 5

# Override my settings usign Django Settings
for var_name, value in dict(locals()).items():
    if var_name.isupper():
        locals()[var_name] = getattr(settings, var_name, value)
