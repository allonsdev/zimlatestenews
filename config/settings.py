"""
Django settings for config project — ZimLatestNews
"""

from pathlib import Path
from decouple import config
import cloudinary
import dj_database_url

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

SECRET_KEY = config('SECRET_KEY', default='django-insecure-23cp3qcg8#bakvq--rdtnn2f46-7)e)o-g@w1&pty-px=%(s74')

DEBUG = True

ALLOWED_HOSTS = ['*']

# ---------------------------------------------------------------------------
# Installed apps
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    # Third-party
    'whitenoise.runserver_nostatic',
    'ckeditor',
    'ckeditor_uploader',
    'taggit',
    'cloudinary',
    'cloudinary_storage',

    # Your apps
    'articles',
    'categories',
    'pages',
    'ads',
]


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

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
                'django.template.context_processors.media',
                'articles.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ---------------------------------------------------------------------------
# Database
# Switch USE_POSTGRES = True when deploying, False for local SQLite
# ---------------------------------------------------------------------------

USE_POSTGRES = config('USE_POSTGRES', default=True, cast=bool)

if USE_POSTGRES:
    DATABASES = {
        'default': dj_database_url.config(
            default='postgresql://postgres.hgvwxfzaqjyooafgjhpq:Tafadzwa22.@aws-0-eu-west-1.pooler.supabase.com:6543/postgres'
        )
    }
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Harare'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True


# ---------------------------------------------------------------------------
# Media files
# ---------------------------------------------------------------------------

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------------------------------------------------------------------------
# Cloudinary
# ---------------------------------------------------------------------------

cloudinary.config(
    cloud_name = "dlpce7ugr",
    api_key    = "113441941361137",
    api_secret = "Yn0DwsVZ34EySWFbNxtL9s3wUfw",
    secure     = True,
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dlpce7ugr',
    'API_KEY':    '113441941361137',
    'API_SECRET': 'Yn0DwsVZ34EySWFbNxtL9s3wUfw',
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


# ---------------------------------------------------------------------------
# CKEditor
# ---------------------------------------------------------------------------

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike'],
            ['NumberedList', 'BulletedList', 'Blockquote'],
            ['Link', 'Unlink'],
            ['Image', 'Table', 'HorizontalRule'],
            ['Format', 'FontSize'],
            ['Source'],
        ],
        'height': 400,
        'width': '100%',
        'extraPlugins': 'uploadimage',
    },
}


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL', default='ZimLatestNews <noreply@zimlatestnews.online>')
SERVER_EMAIL        = DEFAULT_FROM_EMAIL


# ---------------------------------------------------------------------------
# Default primary key
# ---------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# SEO
# ---------------------------------------------------------------------------

SITE_NAME                   = 'ZimLatestNews'
META_SITE_PROTOCOL          = 'https'
META_USE_OG_PROPERTIES      = True
META_USE_TWITTER_PROPERTIES = True