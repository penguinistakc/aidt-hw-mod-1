"""Django settings for the project.

This settings module follows best practices:
- Uses environment variables for secrets and environment-dependent settings
- Configures templates and static files directories
- Defaults to SQLite locally with optional DATABASE_URL support
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    """Fetch a boolean environment variable.

    Accepts common truthy values: '1', 'true', 'yes', 'on'.
    """
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_database_url(url: str) -> Dict[str, Any]:
    """Very small DATABASE_URL parser supporting postgres and sqlite.

    Prefer using Django's `django-environ` or `dj-database-url` in larger projects,
    but avoid third-party deps here per guidelines.
    """
    if url.startswith("sqlite://"):
        # sqlite:///absolute/path or sqlite:///<relative>
        path = url.replace("sqlite:///", "")
        if not Path(path).is_absolute():
            path = str(BASE_DIR / path)
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": path}

    if url.startswith("postgres://") or url.startswith("postgresql://"):
        # Let Django/psycopg handle parsing pieces via NAME/USER/etc if needed.
        # For simplicity, provide URL directly via OPTIONS.
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("PGDATABASE", ""),
            "USER": os.getenv("PGUSER", ""),
            "PASSWORD": os.getenv("PGPASSWORD", ""),
            "HOST": os.getenv("PGHOST", ""),
            "PORT": os.getenv("PGPORT", ""),
            # As a lightweight fallback, don't rely on full URL parsing.
        }

    raise ValueError("Unsupported DATABASE_URL scheme. Use sqlite:/// or postgresql://")


SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-secret-key-change-me")
DEBUG = env_bool("DEBUG", default=True)

raw_allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
ALLOWED_HOSTS: List[str] = [h.strip() for h in raw_allowed_hosts.split(",") if h.strip()]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# Database
database_url = os.getenv("DATABASE_URL")
if database_url:
    try:
        DATABASES = {"default": parse_database_url(database_url)}
    except ValueError:
        # Fallback to SQLite on parse errors to avoid crashes in local dev
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(BASE_DIR / "db.sqlite3"),
            }
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
