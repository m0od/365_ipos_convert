from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import current_time

db = SQLAlchemy()


class TenAntConfig(db.Model):
    __bind_key__ = 'ipos365'
    __tablename__ = 'config'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    domain = db.Column(db.Text, default=None)
    user = db.Column(db.Text, default=None)
    password = db.Column(db.Text, default=None)
    cookie = db.Column(db.Integer, default=None)
    token = db.Column(db.Text, default=None)
    branch = db.Column(db.Text, default=None)
    store = db.Column(db.Integer, default=None)
    vat = db.Column(db.Float, default=0.08)
    mail = db.Column(db.Boolean, default=True)


class Log(db.Model):
    __bind_key__ = 'ipos365'
    __tablename__ = 'log'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    configId = db.Column(db.Integer, default=None)
    branch = db.Column(db.Text, default=None)
    store = db.Column(db.Integer, default=None)
    code = db.Column(db.Text, default=None)
    content = db.Column(db.JSON, default=None)
    rid = db.Column(db.VARCHAR, default=None)
    status = db.Column(db.Integer, default=None)
    result = db.Column(db.Text, default=None)
    log_date = db.Column(db.DateTime, default=current_time())
    type = db.Column(db.Integer, default=1)
    hash = db.Column(db.DECIMAL(64, 0), default=None)


class TechLog(db.Model):
    __bind_key__ = 'ipos365'
    __tablename__ = 'log_technical'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    rid = db.Column(db.VARCHAR, default=None)
    log_date = db.Column(db.DateTime, default=current_time())
    task_name = db.Column(db.Text, default=None)
    state = db.Column(db.Text, default=None)
    info = db.Column(db.JSON, default=None)


class TenAntPayment(db.Model):
    __bind_key__ = 'ipos365'
    __tablename__ = 'payment'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    configId = db.Column(db.Integer)
    name = db.Column(db.Text, default=None)
    accountId = db.Column(db.Integer, default=None)


class TenAntProduct(db.Model):
    __bind_key__ = 'ipos365'
    __tablename__ = 'product'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    configId = db.Column(db.Integer)
    code = db.Column(db.Text, default=None)
    productId = db.Column(db.Integer, default=0)

#
# class Order(db.Model):
#     __bind_key__ = 'ipos365'
#     __tablename__ = 'order'
#     id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
#     configId = db.Column(db.Integer)
#     code = db.Column(db.Text, default=None)
#     orderId = db.Column(db.Integer, default=None)
