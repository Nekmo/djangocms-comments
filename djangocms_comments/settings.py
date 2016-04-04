from django.conf import settings

AKISMET_API_KEY = ''

# Override my settings usign Django Settings
for var_name, value in locals().items():
    if not var_name.isupper():
        continue
    locals()[var_name] = getattr(settings, var_name, value)
