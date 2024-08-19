"""
WSGI config for queueproto project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

from django.conf import settings
from django.core.wsgi import get_wsgi_application

from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "queueproto.settings")

application = get_wsgi_application()

fastapp_v1_root = "/api/v1"
fastapp_v1 = FastAPI()

fastapp_v1.mount("/static", StaticFiles(directory=settings.BASE_DIR / "static"), name="static")

origins = [
    "http://localhost:8000/",
    "https://localhost:8000/",
    "http://localhost:5173/",
    "https://localhost:5173/",
]

fastapp_v1.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.v1.routers.core import router as queue_router

fastapp_v1.include_router(
    queue_router, prefix=f"{fastapp_v1_root}/core"
)

@fastapp_v1.get(f"{fastapp_v1_root}/healthcheck", include_in_schema=False)
def healthcheck():
    return {"status": "We are up and running, baby!"}


fastapp_v1.mount("/", WSGIMiddleware(application))
