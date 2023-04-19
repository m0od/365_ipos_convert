import hashlib
import json
import uuid
from common_celery import convert
from datetime import datetime
from flask import request, Blueprint, abort, render_template, Response
from flask_sqlalchemy import SQLAlchemy

from model import TenAntConfig, Log, TenAntProduct, TenAntPayment
from pos365api import API


class MissingInformationException(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


db = SQLAlchemy()
common = Blueprint('common', __name__)


@common.route('/cfg', methods=['PATCH'])
def update_cfg():
    id = request.form.get('cfgId')
    cookie = request.form.get('cookie')
    cfg = TenAntConfig.query.filter_by(id=id).first()
    if cfg is not None:
        cfg.cookie = cookie
        try:
            db.session.commit()
        except:
            db.session.rollback()
    return {}


@common.route('/log', methods=['POST'])
def update_log():
    rid = request.json.get('rid')
    result = request.json.get('result')
    log = Log.query.filter_by(rid=rid).first()
    if log is not None:
        log.result = result
        try:
            db.session.commit()
        except:
            db.session.rollback()
    return {}


@common.route('/product', methods=['POST', 'GET'])
def product():
    id = request.args.get('cfgId')
    code = request.args.get('code')
    if request.method == 'GET':
        p = TenAntProduct.query.filter(TenAntProduct.configId == id, TenAntProduct.code == code).first()
        if p is not None:
            return {
                'status': True,
                'Id': p.productId
            }
        return {'status': False}
    elif request.method == 'POST':
        pid = request.args.get('pid')
        p = TenAntProduct.query.filter(TenAntProduct.configId == id, TenAntProduct.code == code).first()
        if p is None:
            p = TenAntProduct()
            p.code = code
            p.configId = id,
            p.productId = pid
            try:
                db.session.add(p)
                db.session.commit()
            except:
                db.session.rollback()
        return {}
    return abort(404)


@common.route('/payment', methods=['GET', 'POST'])
def get_payment():
    id = request.args.get('cfgId')
    name = request.args.get('name')
    if request.method == 'GET':
        al = TenAntPayment.query.filter(TenAntPayment.configId == id, TenAntPayment.name == name).first()
        if al is not None:
            return {
                'status': True,
                'AccountId': al.accountId
            }

        return {'status': False}
    elif request.method == 'POST':
        accId = request.args.get('accId')
        al = TenAntPayment.query.filter(TenAntPayment.configId == id, TenAntPayment.name == name).first()
        if al is None:
            al = TenAntPayment()
            al.configId = id
            al.name = name
            al.accountId = accId
            try:
                db.session.add(al)
                db.session.commit()
            except:
                db.session.rollback()
        return {}
    return abort(404)


@common.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'GET':
        l = Log()
        l.rid = str(uuid.uuid4())
        try:
            db.session.add(l)
            db.session.commit()
        except:
            db.session.rollback()
        token = request.args.get('token')
        if token == 'kt365aA@123':
            return render_template('setup.html')
        else:
            return abort(404)
    else:
        token = request.form.get('token')
        branch = request.form.get('branch')
        domain = request.form.get('domain')
        user = request.form.get('user')
        password = request.form.get('password')
        cfg = TenAntConfig.query.filter_by(branch=branch).first()
        api = API(domain=domain, user=user, password=password)
        session = api.auth()
        if cfg is None:
            cfg = TenAntConfig()
            try:
                db.session.add(cfg)
            except:
                db.session.rollback()
        cfg.branch = branch
        cfg.domain = domain
        cfg.user = user
        cfg.password = password
        cfg.token = hashlib.sha256(str(uuid.uuid4()).encode('utf-8')).hexdigest()
        try:
            db.session.commit()
        except:
            db.session.rollback()
        cfg.cookie = session
        for k, v in api.account_list()['accounts'].items():
            pm = TenAntPayment.query.filter(TenAntPayment.configId == cfg.id, TenAntPayment.name == k).first()
            if pm is None:
                pm = TenAntPayment()
                pm.name = k
                pm.accountId = v
                pm.configId = cfg.id
                try:
                    db.session.add(pm)
                    db.session.commit()
                except:
                    db.session.rollback()
        return {'status': True, 'retailer': cfg.branch, 'token': cfg.token}


@common.route('/orders', methods=['POST'])
def orders():
    branch = request.headers.get('Retailer').lower()
    token = request.headers.get('Authorization').lower()
    cfg = TenAntConfig.query.filter_by(branch=branch).first()
    if cfg is None or cfg.token != token:
        return abort(403)
    try:
        content = request.json
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{branch} {now} -> {content}")
        log = Log()
        log.branch = branch
        log.code = content.get('Code')
        log.content = str(content)
        log.log_date = datetime.now()
        try:
            db.session.add(log)
            db.session.commit()
        except:
            db.session.rollback()
        if content.get('Code') is None or len(str(content.get('Code').strip())) == 0:
            raise MissingInformationException('Thiếu thông tin mã đơn hàng (Code)')
        if content.get('PurchaseDate') is None or len(str(content.get('PurchaseDate').strip())) == 0:
            raise MissingInformationException('Thiếu thông tin ngày bán (PurchaseDate)')
        if content.get('PaymentMethods') is None or type(content.get('PaymentMethods')) != list:
            return MissingInformationException('Thiếu thông tin PTTT (PaymentMethods)')
        for pm in content.get('PaymentMethods'):
            if type(pm) != dict:
                raise MissingInformationException('Thông tin PTTT không hợp lệ')
        if content.get('AdditionalServices') is not None:
            if type(content.get('AdditionalServices')) != list:
                raise MissingInformationException('Thông tin Phụ phí không hợp lệ')
            for service in content.get('AdditionalServices'):
                if type(service) != dict:
                    raise MissingInformationException('Thông tin Phụ phí không hợp lệ')
        result = convert.delay(cfg.domain, cfg.id, cfg.cookie, content, cfg.user, cfg.password)
        log.rid = str(result.id)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return {"result_id": result.id}
    except Exception as e:
        return Response(json.dumps({'message': str(e)}), status=400, mimetype='application/json')


@common.route("/result/<id>", methods=['GET'])
def task_result(id):
    task = convert.AsyncResult(id)
    if task.state == 'PENDING':
        response = {
            'status': str(task.state)
        }
        response = Response(json.dumps(response), status=201, mimetype='application/json')
    elif task.state != 'FAILURE':
        response = {
            'state': task.state
        }
        if task.info['status'] is True:
            response['state'] = 'SUCCESS'
            response['result'] = task.info['result']
            response = Response(json.dumps(response), status=200, mimetype='application/json')
        else:
            response['state'] = 'FAILURE'
            response['reason'] = task.info['result']
            response = Response(json.dumps(response), status=400, mimetype='application/json')

    else:
        response = {
            'state': task.state
        }
        response = Response(json.dumps(response), status=400, mimetype='application/json')
    return response
