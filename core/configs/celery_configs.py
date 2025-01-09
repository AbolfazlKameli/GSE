from datetime import timedelta

from decouple import config

broker_connection_retry_on_startup = True

broker_url = config('CELERY_REDIS_LOCATION')
result_backend = config('CELERY_REDIS_LOCATION')

worker_prefetch_multiplier = 3

timezone = config('TIME_ZONE')

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json', 'json']
result_expire = timedelta(minutes=1)
