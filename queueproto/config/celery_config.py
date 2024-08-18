from django.conf import settings

broker_url = settings.CELERY_BROKER_URL
result_backend = settings.CELERY_BROKER_URL

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = settings.CELERY_TIME_ZONE
enable_utc = True
broker_connection_retry_on_startup = True
