import decimal
import hashlib
import json
import uuid

import requests
from pymongo import MongoClient
from sqlalchemy import or_
from sqlalchemy.sql.functions import current_time

from common_celery import convert, add_payment, delData, addUser
from datetime import datetime, timedelta
from flask import request, Blueprint, abort, render_template, Response, send_file, jsonify, redirect, url_for, session
# from flask_sqlalchemy import SQLAlchemy
from model import TenAntConfig, Log, TenAntProduct, TenAntPayment, db
from pos365api import API
# from mongo import db_mongo


class MissingInformationException(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


# db = SQLAlchemy()
common = Blueprint('common', __name__)


@common.route('/add_user', methods=['POST'])
def add_user():
    print(request.form)
    if request.form.get('token') != 'kt365aA@123':
        return abort(403)
    user = request.form.get('user')
    if not user: return abort(403)
    user = str(user).strip()
    if not len(user): return abort(403)
    print(user)
    pw = request.form.get('password')
    if not pw: return abort(403)
    pw = str(pw).strip()
    if not len(pw): return abort(403)
    print(pw)
    user_type = request.form.get('type')
    if not user_type: return abort(403)
    user_type = str(user_type).strip()
    if not len(user_type): return abort(403)
    if user_type != 'FTP' and user_type != 'FTPS':
        return abort(403)
    print(user_type)
    addUser.delay(user, pw, user_type)
    return {}

# @local_only
@common.route('/cfg', methods=['PATCH'])
def local_update_cfg():
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
def local_update_log():
    rid = request.json.get('rid')
    result = request.json.get('result')
    # mongo = MongoClient('localhost').adapter.log
    # l = mongo.find_one({'rid': rid})
    # if l is not None:
    #     update = {'result'}
    #     log.result = result
    #     if result.startswith("{'status': False"):
    #         log.status = False
    #     else:
    #         log.status = True
    #     try:
    #         db.session.commit()
    #     except:
    #         db.session.rollback()
    log = Log.query.filter_by(rid=rid).first()
    if log is not None:
        log.log_date = current_time()
        log.status = None
        try:
            if result.startswith("{'status': False"):
                log.status = 0
                log.result = result
            elif result.startswith("{'status': True"):
                log.status = 1
                log.result = result
        except:
            log.status = None
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return abort(403)
        return {'status': True}
    return {'status': False}


@common.route('/mail', methods=['GET'])
def report_mail():
    token = request.args.get('token')
    if token != 'kt365aA@123':
        return abort(404)
    cfg = TenAntConfig.query.filter_by(mail=True).all()
    if cfg is not None:
        ret = []
        for _ in cfg:
            ret.append(_.domain)
        return ret
    return {}


@common.route('/product', methods=['POST', 'GET'])
def local_product():
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
def local_get_payment():
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

@common.route('/fetch_log', methods=['GET'])
def fetch_log():
    token = request.args.get('token')
    if token != 'kt365aA@123':
        return abort(404)
    now = datetime.now()
    now = now.replace(second=0, microsecond=0)
    begin = now - timedelta(minutes=10)
    # begin = now.replace(hour=17,minute=9, second=39)
    logs = Log.query.filter(Log.rid != None,
                            Log.log_date >= begin,
                            or_(Log.status == None, Log.status == 0))
    logs = logs.join(TenAntConfig, TenAntConfig.id == Log.configId)
    logs = logs.add_columns(TenAntConfig.token)
    logs = logs.all()
    ret = []
    for l in logs:
            try:
                ret.append({
                    'retailer': l.Log.branch,
                    'token': l.token,
                    'store': l.Log.store,
                    'content': l.Log.content,
                    'type': l.Log.type
                })
            except Exception as e:
                print(e)
            # return jsonify([(str(e))])
            # print(content)
    return jsonify(ret)



@common.route('/setup', methods=['GET', 'POST'])
def setup():
    # return 'andwedawdawd'
    if request.method == 'GET':
        token = request.args.get('token')
        if token == 'kt365aA@123':
            return render_template('setup.html')
        else:
            return abort(404)
        # return render_template('setup.html')
    else:
        # return jsonify({
        #     'abc': 12456
        # })
        try:
            token = request.form.get('token')
            if token != 'kt365aA@123':
                return abort(403)
            branch = request.form.get('branch')
            if branch and len(branch.lower().strip()):
                branch = branch.lower().strip()
                domain = request.form.get('domain')
                user = request.form.get('user')
                password = request.form.get('password')
                api = API(domain=domain, user=user, password=password)
                session = api.auth()
                if session is not None:
                    cfg = TenAntConfig.query.filter_by(branch=branch).first()
                    if cfg is None:
                        cfg = TenAntConfig()
                        try:
                            db.session.add(cfg)
                        except:
                            db.session.rollback()
                    cfg.cookie = session
                    cfg.branch = branch
                    cfg.domain = domain
                    cfg.user = user
                    cfg.password = password
                    if cfg is not None:
                        cfg.token = hashlib.sha256(str(uuid.uuid4()).encode('utf-8')).hexdigest()
                    try:
                        db.session.commit()
                    except:
                        db.session.rollback()
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
                    return {'status': True, 'retailer': cfg.branch, 'authorization': cfg.token}
                else:
                    return {'status': False, 'message': 'Login Pos 365 Failed'}
            else:
                domain = request.form.get('domain')
                user = request.form.get('user')
                password = request.form.get('password')
                since = request.form.get('since')
                since = datetime.strptime(since, '%Y-%m-%d')
                before = request.form.get('before')
                before = datetime.strptime(before, '%Y-%m-%d')
                # since = since - timedelta(days=1)
                # since = since.strftime('%Y-%m-%dT17:00:00Z')
                # before = before.strftime('%Y-%m-%dT16:59:00Z')
                # _filter = []
                # _filter += ['(', 'Status', 'eq', '2', 'or']
                # _filter += ['Status', 'eq', '0', ')']
                # _filter += ['and']
                # _filter += ['PurchaseDate', 'ge']
                # _filter += [f"'datetime''{since}'''"]
                # _filter += ['and']
                # _filter += ['PurchaseDate', 'lt']
                # _filter += [f"'datetime''{before}'''"]
                # print(*_filter)
                delData.delay(domain, user, password, since, before)

                return {'status': True}
        except Exception as e:
            return {'status': str(e)}

@common.route('/add_methods', methods=['POST'])
def add_methods():
    try:
        branch = request.headers.get('Retailer').lower()
        if branch is None: return abort(403)
        token = request.headers.get('Authorization').lower()
        if token is None: return abort(403)
    except:
        return abort(403)
    store = request.headers.get('Store')
    cfg = TenAntConfig.query.filter(TenAntConfig.branch == branch).first()
    if cfg is None or cfg.token != token:
        return abort(403)
    try:
        content = request.json
        hash = decimal.Decimal(int(hashlib.md5(content.get('OrderCode').encode('utf-8')).hexdigest(), 16))
        now = datetime.now().replace(second=0, microsecond=0)
        begin = datetime.now() - timedelta(minutes=10)
        log = db.session.query(Log).filter(Log.hash == hash,
                                           Log.rid is not None,
                                           Log.log_date >= begin).first()
        if log is not None:
            if log.status is None:
                return Response(json.dumps({'message': 'duplicate'}), status=400, mimetype='application/json')
        # now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log = Log()
        log.configId = cfg.id
        log.branch = branch
        log.store = store
        log.code = content.get('OrderCode')
        log.content = content
        log.hash = hash
        log.type = 2
        try:
            db.session.add(log)
            db.session.commit()
        except:
            db.session.rollback()
        result = add_payment.delay(cfg.domain, cfg.id, cfg.cookie, content, cfg.user, cfg.password)
        log.rid = str(result.id)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return {'result_id': result.id}
    except Exception as e:
        print(e)
        return Response(json.dumps({'message': str(e)}), status=400, mimetype='application/json')


@common.route('/orders', methods=['POST'])
def orders():

    try:
        # f = open('ipos.txt', 'a')
        # f.write(str(request.headers))
        # f.close()
        branch = request.headers.get('Retailer').lower()
        if branch is None: return abort(403)
        token = request.headers.get('Authorization').lower()
        if token is None: return abort(403)
    except:
        return abort(403)
    store = request.headers.get('Store')
    cfg = TenAntConfig.query.filter(TenAntConfig.branch == branch).first()
    if cfg is None or cfg.token != token:
        return abort(403)
    try:
        content = request.json
        # now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # print(f"{branch} {now} -> {content}")
        hash = decimal.Decimal(int(hashlib.md5(content.get('Code').encode('utf-8')).hexdigest(), 16))
        now = datetime.now().replace(second=0, microsecond=0)
        begin = datetime.now() - timedelta(minutes=10)
        log = db.session.query(Log).filter(Log.hash == hash,
                                           # Log.rid is not None,
                                           Log.log_date >= begin).first()
        if log is not None:
            if log.status == -1:
                return Response(json.dumps({'message': 'duplicate'}), status=200, mimetype='application/json')
        if content.get('Code') is None or len(str(content.get('Code').strip())) == 0:
            raise MissingInformationException('Thiếu thông tin mã đơn hàng (Code)')
        if content.get('PurchaseDate') is not None and len(str(content.get('PurchaseDate').strip())) == 0:
            raise MissingInformationException('Thiếu thông tin ngày bán (PurchaseDate)')
        if content.get('ReturnDate') is not None and len(str(content.get('ReturnDate').strip())) == 0:
            raise MissingInformationException('Thiếu thông tin ngày bán (ReturnDate)')
        if content.get('PaymentMethods') is None or type(content.get('PaymentMethods')) != list:
            return MissingInformationException('Thiếu thông tin PTTT (PaymentMethods)')
        if store and int(store) in [15548, 26451, 14928]:
            if content.get('Voucher') != 0:
                content['PaymentMethods'].append({
                    'Name': 'VOUCHER', 'Value': content.get('Voucher')
                })
                content.pop('Voucher')
                content.pop('VoucherCode')
        now = datetime.now()
        for pm in content.get('PaymentMethods'):
            if type(pm) != dict:
                raise MissingInformationException('Thông tin PTTT không hợp lệ')
        if content.get('AdditionalServices') is not None:
            # print(content.get('AdditionalServices'))
            if type(content.get('AdditionalServices')) != list:
                raise MissingInformationException('Thông tin Phụ phí không hợp lệ')
            for service in content.get('AdditionalServices'):
                if type(service) != dict:
                    raise MissingInformationException('Thông tin Phụ phí không hợp lệ')
        if request.headers.get('debug') != 'kt365aA@123' \
                and content.get('PurchaseDate') is not None \
                and datetime.strptime(content.get('PurchaseDate'),
                                      '%Y-%m-%d %H:%M:%S') < now - timedelta(days=1, hours=12):
            return {'result_id': '00000000-0000-0000-0000-000000000000'}
        log = Log()
        log.configId = cfg.id
        log.branch = branch
        log.store = store
        log.code = content.get('Code')
        log.content = content
        log.type = 1
        log.hash = hash
        log.status = -1
        try:
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        result = convert.delay(cfg.domain, cfg.id, cfg.cookie, content, cfg.user, cfg.password, cfg.vat)
        log.rid = str(result.id)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return {'result_id': result.id}
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
