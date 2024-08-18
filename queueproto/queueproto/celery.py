import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "queueproto.settings")

app = Celery("queueproto")

app.config_from_object("config.celery_config")

@app.task(bind=True, ignore_result=True)
def health_check(self):
   print(f"Request {self.request!r}")
