import os

# from pymongo import MongoClient

# from flask_socketio import SocketIO

from common_web import common
from model import db
from flask import Flask, request, abort

# from notification import noti
from technical_api import technical

with open('../.secret_key', 'a+b') as secret:
    secret.seek(0)  # Seek to beginning of file since a+ mode leaves you at the end and w+ deletes the file
    key = secret.read()
    if not key:
        key = os.urandom(64)
        secret.write(key)
        secret.flush()


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or key
    JSON_SORT_KEYS = False
    SQLALCHEMY_BINDS = {
        'ipos365': 'mysql://root:7y!FY^netG!jn>f+@localhost/adap_db?charset=utf8mb4',
    }

    SQLALCHEMY_ECHO = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    GOOGLE_CLIENT_ID = '263581281598-tkh7tha61k78kb55c670sjfu6651m3a1.apps.googleusercontent.com'
    # MONGO_URI = 'mongodb://localhost:27017/adapter'


# wss = SocketIO()
def create_app(config=Config):
    # print(123123123)
    app = Flask(__name__)
    # client = MongoClient('localhost')
    app.config.from_object(config)
    db.init_app(app)
    app.db = db
    # app.db = client.adapter
    init_utils(app)
    app.register_blueprint(common)
    # app.register_blueprint(technical)
    # app.register_blueprint(noti)
    # app.init_app(app)
    # init_utils(app)
    return app


def init_utils(app):
    @app.before_request
    def local_only():
        if not app.debug:
            try:
                functions = app.view_functions[request.endpoint]

                if functions.__name__.startswith('local_') \
                        and request.remote_addr not in ['127.0.0.1', '103.176.145.241']:
                    abort(404)
                # if functions.__name__.startswith('api_') and request.remote_addr not in ['117.4.244.167', '118.70.124.165']:
                #     abort(404)
            except KeyError as e:
                print(e)
                abort(404)
