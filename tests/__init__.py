import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evaluation_registry.settings")
django.setup()
