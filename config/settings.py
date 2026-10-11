"""
Django settings for the Northpreneur Hub Ltd corporate website.
"""

import sys
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',

    'django_ckeditor_5',

    'sitecore',
    'organization',
    'services',
    'programs',
    'blog',
    'contact',
    'pages',
    'accounts',
    'learning',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sitecore.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True


# Static & media files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# The manifest storage needs `collectstatic` to have run; tests render templates without it.
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    STORAGES['staticfiles'] = {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Student accounts — sign in with email; admin keeps its own /admin/login/.
AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'sitecore:home'

# Security hardening (relaxed automatically by DEBUG where appropriate)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
# Decoupled from DEBUG on purpose: a freshly deployed prod site often runs DEBUG=False
# behind plain HTTP for a while (DNS/cert not live yet) — forcing Secure cookies at that
# point silently breaks admin login and CSRF everywhere. Flip SECURE_SSL_REDIRECT (and
# leave these at their default True) once HTTPS is actually serving the site.
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=not DEBUG, cast=bool)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)

# Email — Gmail SMTP, same setup as the GIIA project (use a Gmail *app password*).
# Falls back to printing emails to the console until EMAIL_HOST_USER is set.
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_BACKEND = config('EMAIL_BACKEND', default=(
    'django.core.mail.backends.smtp.EmailBackend' if EMAIL_HOST_USER
    else 'django.core.mail.backends.console.EmailBackend'))
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER or 'no-reply@northpreneurhub.com.ng')
CONTACT_NOTIFICATION_EMAIL = config('CONTACT_NOTIFICATION_EMAIL', default='hello@northpreneurhub.com.ng')

# django-ckeditor-5 configuration — a curated toolbar, no image-upload endpoint
# (images are attached via each model's own ImageField instead).
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'underline', 'link', '|',
            'bulletedList', 'numberedList', 'blockQuote', '|',
            'undo', 'redo',
        ],
    },
    'richtext': {
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'underline', 'link', '|',
            'bulletedList', 'numberedList', 'blockQuote', 'insertTable', '|',
            'undo', 'redo',
        ],
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells'],
        },
    },
}
CKEDITOR_5_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Site-wide constants used by templates/context processor
SITE_DOMAIN = config('SITE_DOMAIN', default='127.0.0.1:8000')
SITE_PROTOCOL = config('SITE_PROTOCOL', default='http')

# Zainpay — course payments, same integration as the GIIA project (see payments/zainpay.py).
# ZAINPAY_BASE_URL: https://sandbox.zainpay.ng for testing, https://api.zainpay.ng live —
# the keys must belong to the same environment as the Zainbox. Leave the keys blank and
# paid courses show "payment not available" instead of failing.
ZAINPAY_PUBLIC_KEY = config('ZAINPAY_PUBLIC_KEY', default='')
ZAINPAY_SECRET_KEY = config('ZAINPAY_SECRET_KEY', default='')
ZAINPAY_BASE_URL = config('ZAINPAY_BASE_URL', default='https://sandbox.zainpay.ng')
ZAINPAY_ZAINBOX_CODE = config('ZAINPAY_ZAINBOX_CODE', default='')
# The Zainbox's settlement account, searched to confirm payments. Optional: looked up
# from Zainpay automatically when blank.
ZAINPAY_ACCOUNT_NUMBER = config('ZAINPAY_ACCOUNT_NUMBER', default='')
