# flake8: noqa
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .settings_base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

VCAP_APPLICATION = env.json("VCAP_APPLICATION", default={})
BASE_URL = env.str("BASE_URL")
COLA_COOKIE_NAME = env.str("COLA_COOKIE_NAME", "")
COLA_COOKIE_DOMAIN = env.str("COLA_COOKIE_DOMAIN", "")
COLA_COGNITO_CLIENT_ID = env.str("COLA_COGNITO_CLIENT_ID", "")
AWS_REGION_NAME = env.str("AWS_REGION_NAME", "")
COLA_COGNITO_USER_POOL_ID = env.str("COLA_COGNITO_USER_POOL_ID", "")
COLA_LOGIN_URL = env.str("COLA_LOGIN_URL", "")
COLA_JWT_EXTRACTION_REGEX_PATTERN = env.str("COLA_JWT_EXTRACTION_REGEX_PATTERN", r"")


# Application definition


CORS_MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
]


if DEBUG:
    MIDDLEWARE = MIDDLEWARE + CORS_MIDDLEWARE


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST"),
        "PORT": env.str("POSTGRES_PORT"),
        "ATOMIC_REQUESTS": True,
        "DISABLE_SERVER_SIDE_CURSORS": True,
    }
}

AUTHENTICATION_BACKENDS = [
    "automatilib.cola.backend.COLAAuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
]


if not DEBUG:
    SENTRY_DSN = env.str("SENTRY_DSN", default="")
    SENTRY_ENVIRONMENT = env.str("SENTRY_ENVIRONMENT", default="")

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        environment=SENTRY_ENVIRONMENT,
        send_default_pii=False,
        traces_sample_rate=1.0,
        profiles_sample_rate=0.0,
    )


if not DEBUG:
    SECURE_HSTS_SECONDS = 2 * 365 * 24 * 60 * 60  # Mozilla's guidance max-age 2 years
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True


# Email

EMAIL_BACKEND_TYPE = env.str("EMAIL_BACKEND_TYPE")

if EMAIL_BACKEND_TYPE == "FILE":
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = env.str("EMAIL_FILE_PATH")
elif EMAIL_BACKEND_TYPE == "CONSOLE":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
elif EMAIL_BACKEND_TYPE == "GOVUKNOTIFY":
    EMAIL_BACKEND = "django_gov_notify.backends.NotifyEmailBackend"
    GOVUK_NOTIFY_API_KEY = env.str("GOVUK_NOTIFY_API_KEY")
    GOVUK_NOTIFY_PLAIN_EMAIL_TEMPLATE_ID = env.str("GOVUK_NOTIFY_PLAIN_EMAIL_TEMPLATE_ID")
else:
    if EMAIL_BACKEND_TYPE not in ("FILE", "CONSOLE", "GOVUKNOTIFY"):
        raise Exception(f"Unknown EMAIL_BACKEND_TYPE of {EMAIL_BACKEND_TYPE}")

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    SESSION_EXPIRE_AT_BROWSER_CLOSE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_AGE = 60 * 60 * 24 * 120  # 120 days
    SESSION_COOKIE_SAMESITE = "Strict"
