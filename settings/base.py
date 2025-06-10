import os
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-c4a^r3!(iqpr=^4aakno!l71d*5$x#)gc8vo2iqh#$5evg$9vg"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "bessiestressriskassessment.com"]

AUTH_USER_MODEL = "users.User"

# Load all environment variables
dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path)

# Get MySQL connection details
DBHOST = os.getenv("DBHOST")
DBPORT = os.getenv("DBPORT")
DBNAME = os.getenv("DBNAME")
DBUSER = os.getenv("DBUSER")
DBPASS = os.getenv("DBPASS")
EMAILHOST = os.getenv("EMAILHOST")
EMAILPORT = os.getenv("EMAILPORT")
EMAILUSER = os.getenv("EMAILUSER")
EMAILPASSWORD = os.getenv("EMAILPASSWORD")

# Site domain settings for email URLs
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "http://localhost:8000")

# Database... If postgresql envs are not set, use sqlite3
if DBHOST and DBPORT and DBNAME and DBUSER and DBPASS:
  DATABASES = {
      "default": {
          "ENGINE": "django.db.backends.postgresql",
          "NAME": DBNAME,
          "USER": DBUSER,
          "PASSWORD": DBPASS,
          "HOST": DBHOST,
          "PORT": DBPORT,
      }
  }
else:
  DATABASES = {
      "default": {
          "ENGINE": "django.db.backends.sqlite3",
          "NAME": BASE_DIR / "db.sqlite3",
      }
  }

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = EMAILHOST
EMAIL_PORT = EMAILPORT
EMAIL_HOST_USER = EMAILUSER
EMAIL_HOST_PASSWORD = EMAILPASSWORD
DEFAULT_FROM_EMAIL = "no-reply@bessiestressriskassessment.com"
SERVER_EMAIL = "no-reply@bessiestressriskassessment.com"


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "background_task",
    "users",
    "mini_bessie",
    "bessie",
    "pages",
    "formtools",
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
]

ROOT_URLCONF = "bessie_tech.urls"

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
    },
]

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django.db.backends': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#         },
#     },
# }


WSGI_APPLICATION = "bessie_tech.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en"

LANGUAGES = (("en", "English"),)

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "/dashboard"
LOGOUT_REDIRECT_URL = "/"
