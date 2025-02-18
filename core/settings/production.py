from .settings import *

DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

SECRET_KEY = config('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

CORS_ALLOW_ALL_ORIGINS = False
CORS_ORIGIN_WHITELIST = config('CORS_ORIGIN_WHITELIST').split(',')

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
