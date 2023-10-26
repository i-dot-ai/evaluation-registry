from pathlib import Path

import environ

env = environ.Env()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str("DJANGO_SECRET_KEY")

INSTALLED_APPS = [
    "evaluation_registry.evaluations",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [
            BASE_DIR / "evaluation_registry" / "templates",
        ],
        "OPTIONS": {"environment": "evaluation_registry.jinja2.environment"},
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "evaluation_registry" / "templates" / "allauth",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
