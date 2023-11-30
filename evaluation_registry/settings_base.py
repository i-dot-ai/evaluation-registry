import ast
import os
import socket
import subprocess
from pathlib import Path

import environ

env = environ.Env()

if env.str("ENVIRONMENT", None) != "LOCAL":
    LOCALHOST = socket.gethostbyname(socket.gethostname())


def get_environ_vars() -> dict:
    """get env vars from ec2
    https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/custom-platforms-scripts.html
    """
    completed_process = subprocess.run(
        ["/opt/elasticbeanstalk/bin/get-config", "environment"], stdout=subprocess.PIPE, text=True, check=True
    )

    return ast.literal_eval(completed_process.stdout)


if "POSTGRES_HOST" not in os.environ:
    for key, value in get_environ_vars().items():
        env(key, default=value)


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str("DJANGO_SECRET_KEY")

# Add AWS URLS to ALLOWED_HOSTS once known
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "evaluation-registry-dev.eba-izdb4qxe.eu-west-2.elasticbeanstalk.com",
    "evaluation-registry-prod.eba-izdb4qxe.eu-west-2.elasticbeanstalk.com",
    "evaluation-registry.cabinetoffice.gov.uk",
    "dev.evaluation-registry.service.gov.uk",
    "evaluation-registry.service.gov.uk",
    "evaluation-registry.cabinetoffice.gov.uk",
    "dev.evaluation-registry.cabinetoffice.gov.uk",
]

if env.str("ENVIRONMENT", None) != "LOCAL":
    ALLOWED_HOSTS = ALLOWED_HOSTS + [LOCALHOST]

# CSRF settings
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS: list = [
    # Add your dev and prod urls here, without the protocol
]

ROOT_URLCONF = "evaluation_registry.urls"


WSGI_APPLICATION = "evaluation_registry.wsgi.application"


INSTALLED_APPS = [
    "health_check",
    "evaluation_registry.evaluations",
    "automatilib.core.apps.IdotAIConfig",
    "automatilib.cola.apps.ColaAuthConfig",
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
    "simple_history",
    "storages",
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
    "simple_history.middleware.HistoryRequestMiddleware",
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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "evaluations.User"

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "homepage"
LOGIN_URL = "search"


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"


PERMISSIONS_POLICY: dict[str, list] = {
    "accelerometer": [],
    "autoplay": [],
    "camera": [],
    "display-capture": [],
    "encrypted-media": [],
    "fullscreen": [],
    "gamepad": [],
    "geolocation": [],
    "gyroscope": [],
    "microphone": [],
    "midi": [],
    "payment": [],
}


CSP_DEFAULT_SRC = (
    "'self'",
    "s3.amazonaws.com",
    "evaluation-registry-files-dev.s3.amazonaws.com",
    "evaluation-registry-files-prod.s3.amazonaws.com",
    "'sha256-IfJd5CaJvXieVYkcs/6RUH75vQIASCglGoGoNThv4fg='",
)
CSP_OBJECT_SRC = ("'none'",)
CSP_REQUIRE_TRUSTED_TYPES_FOR = ("'script'",)
# Hash for styles for font in base template
CSP_FONT_SRC = (
    "'self'",
    "s3.amazonaws.com",
    "evaluation-registry-files-dev.s3.amazonaws.com",
    "evaluation-registry-files-prod.s3.amazonaws.com",
)
CSP_STYLE_SRC = (
    "'self'",
    "evaluation-registry-files-dev.s3.amazonaws.com",
    "evaluation-registry-files-prod.s3.amazonaws.com",
)
CSP_FRAME_ANCESTORS = ("'none'",)


CSRF_COOKIE_HTTPONLY = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100 megabytes in bytes
