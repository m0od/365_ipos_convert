from os.path import dirname

from celery import Celery
if __name__:
    import sys

    PATH = dirname(dirname(dirname(__file__)))
    sys.path.append(PATH)
    from tool.app.config import settings



def make_celery():
    celery = Celery(settings.CELERY_NAME)
    celery.conf.update(settings.CELERY_CONFIG)
    return celery
