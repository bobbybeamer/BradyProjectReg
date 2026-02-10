import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'replace-me')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')
# Normalize and ensure common local hosts are present
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS if h.strip()]
for host in ('127.0.0.1', 'localhost', '0.0.0.0', 'testserver'):
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'accounts.apps.AccountsConfig',
    'deals.apps.DealsConfig',
    'notifications.apps.NotificationsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Session optimization
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

ROOT_URLCONF = 'brady_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'brady_portal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        },
        'CONN_MAX_AGE': 600,  # Keep connections open for 10 minutes
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DATE_FORMAT = 'd/m/Y'

# Static files optimization
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Caching configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Logging configuration for production efficiency
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': False,
        },
    },
}
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

# Email
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@brady.example')

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

CORS_ALLOW_ALL_ORIGINS = True

# Deal expiry defaults
DEAL_MIN_EXPIRY_DAYS = int(os.getenv('DEAL_MIN_EXPIRY_DAYS', '90'))
DEAL_MAX_EXPIRY_DAYS = int(os.getenv('DEAL_MAX_EXPIRY_DAYS', '180'))

# Redirects
LOGIN_REDIRECT_URL = '/deals/dashboard/'  # redirects to role-aware dashboard
LOGOUT_REDIRECT_URL = '/accounts/login/'