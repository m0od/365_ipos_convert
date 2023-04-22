from datetime import datetime
import json

from common_web import common
# import celery
# import requests
from model import db
from flask import Flask, request, abort


# from celery import Celery
# from pytz import timezone
# from pos365api import API


class Config(object):
    JSON_SORT_KEYS = False
    SQLALCHEMY_BINDS = {
        'ipos365': 'mysql://root:7y!FY^netG!jn>f+@localhost/ipos365',
    }
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    app.db = db
    init_utils(app)
    app.register_blueprint(common)
    return app


def init_utils(app):
    @app.before_request
    def local_only():
        if not app.debug:
            try:
                functions = app.view_functions[request.endpoint]
                if functions.__name__ in ['setup', 'orders', 'task_result', 'aeon_orders']:
                    return
                if request.remote_addr not in ['127.0.0.1', '103.35.65.114']:
                    abort(404)
            except KeyError as e:
                abort(404)

