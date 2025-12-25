from .settings import *

DEBUG = False

SECRET_KEY = config('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

CORS_ALLOW_ALL_ORIGINS = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST'),
        'PORT': config('POSTGRES_PORT', default=5432),
    }
}

# caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config('REDIS_LOCATION', default="redis://127.0.0.1:6379"),
    }
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static/"

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
