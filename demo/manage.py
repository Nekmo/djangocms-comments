#!/usr/bin/env python
import os
import sys

try:
    import djangocms_comments
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.abspath(__file__), '../../')))
    import djangocms_comments


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo_app.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
