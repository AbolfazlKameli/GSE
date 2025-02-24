import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.settings')

app = Celery('gse')

app.autodiscover_tasks()

app.config_from_object('core.configs.celery_configs')
