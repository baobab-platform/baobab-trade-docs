"""HYB-01 settings. No document issuance, no provider activation, no SQLite fallback."""
import os

SECRET_KEY = os.environ.get("TDOC_SECRET_KEY", "hyb01-development-only-unsafe-key")
DEBUG = os.environ.get("TDOC_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
ROOT_URLCONF = "tdoc_runtime.urls"
INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "tdoc"),
        "USER": os.environ.get("POSTGRES_USER", "tdoc"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 0,
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "UTC"
# The public server is deliberately not configured. Exposing this scaffold
# would bypass the still-unimplemented IAM/CP document PEP.
