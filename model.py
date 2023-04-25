from flask_sqlalchemy import SQLAlchemy
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
    vat = db.Column(db.Float, default=0.1)

class Log(db.Model):
    __bind_key__ = 'ipos365'
    __tablename__ = 'log'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    configId = db.Column(db.Integer, default=None)
    branch = db.Column(db.Text, default=None)
    code = db.Column(db.Text, default=None)
    content = db.Column(db.Text, default=None)
    rid = db.Column(db.VARCHAR, default=None)
    status = db.Column(db.Boolean, default=None)
    result = db.Column(db.Text, default=None)
    log_date = db.Column(db.DateTime, default=None)

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

