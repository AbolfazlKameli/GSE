from datetime import timedelta

from decouple import config

broker_connection_retry_on_startup = True


broker_url = "redis://localhost:6379/1"
result_backend = "redis://localhost:6379/1"

worker_prefetch_multiplier = 3

timezone = config('TIME_ZONE')

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json', 'json']
result_expire = timedelta(minutes=1)
