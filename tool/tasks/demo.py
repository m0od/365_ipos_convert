from celery import Celery
from ..app.config import settings


def make_celery():
    celery = Celery(settings.CELERY_NAME)
    celery.conf.update(settings.CELERY_CONFIG)
    return celery
