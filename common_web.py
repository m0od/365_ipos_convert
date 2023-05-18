import hashlib
import json
import uuid

import requests
from sqlalchemy import or_
from common_celery import convert
from datetime import datetime, timedelta
from flask import request, Blueprint, abort, render_template, Response, send_file, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from model import TenAntConfig, Log, TenAntProduct, TenAntPayment
from pos365api import API
from role import login_required
from google.oauth2 import id_token
from google.auth.transport import requests as ggRequests
from flask import current_app
class MissingInformationException(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


db = SQLAlchemy()
common = Blueprint('common', __name__)

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
    log = Log.query.filter_by(rid=rid).first()
    if log is not None:
        log.result = result
        if result.startswith("{'status': False"):
            log.status = False
        else:
            log.status = True
        try:
            db.session.commit()
        except:
            db.session.rollback()
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
def local_fetch_log():
    token = request.args.get('token')
    if token != 'kt365aA@123':
        return abort(404)
    now = datetime.now()
    now = now.replace(second=0, microsecond=0)
    begin = now - timedelta(minutes=10)
    logs = Log.query.filter(Log.rid != None,
                            Log.log_date >= begin,
                            or_(Log.status == None, Log.status == False))
    logs = logs.join(TenAntConfig, TenAntConfig.id == Log.configId)
    logs = logs.add_columns(TenAntConfig.token)
    logs = logs.all()
    ret = []
    for l in logs:
        content = l.Log.content.replace("\\", '\\\\').replace("'", '"')
        ret.append({
            'retailer': l.Log.branch,
            'token': l.token,
            'store': l.Log.store,
            'content': json.loads(content)
        })
    return jsonify(ret)

# @common.route('/gg_login', methods=['GET', 'POST'])
# def gg_login():
#     form = request.form
#     # GG_CLIENT_ID = '726905584100-o3n5emfgouu6poruvp0r2qb2rkjdfn5b.apps.googleusercontent.com'
#     idinfo = id_token.verify_oauth2_token(form['credential'],
#                                           ggRequests.Request(),
#                                           current_app.config['GOOGLE_CLIENT_ID'])
#
#     # Or, if multiple clients access the backend server:
#     # idinfo = id_token.verify_oauth2_token(token, requests.Request())
#     # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
#     #     raise ValueError('Could not verify audience.')
#
#     # If auth request is from a G Suite domain:
#     # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
#     #     raise ValueError('Wrong hosted domain.')
#     print(idinfo)
#     # ID token is valid. Get the user's Google Account ID from the decoded token.
#     userid = idinfo['sub']
#
#     return ''
@common.route('/', methods=['GET', 'POST'])
def api_technical_department():
    if request.method == 'GET':
        # if session is not None and session.get('accessCode') == 'IT@P0s365kms':
        #     return redirect('/dashboard')
        return render_template('login.html', gg_client_id=current_app.config['GOOGLE_CLIENT_ID'])
    else:
        try:
            info = id_token.verify_oauth2_token(request.form['credential'],
                                                ggRequests.Request(),
                                                current_app.config['GOOGLE_CLIENT_ID'])

            print(info)
            userId = info['sub']
            try:
                session.regenerate()  # NO SESSION FIXATION FOR YOU
            except:
                pass
            session['userId'] = userId
            return redirect('/dashboard')
        except:
            return render_template('login.html')

@common.route('/dashboard', methods=['GET', 'POST'])
@login_required
def api_technical_dashboard():
    return render_template('365.html')
@common.route('/api/orders', methods=['POST'])
def api_orders():
    try:
        code = request.form['code']
        cookie = request.form['cookie']
        link = request.form['link']
        b = requests.session()
        b.headers.update({
            'content-type': 'application/json',
            'cookie': f'ss-id={cookie.strip()}'
        })
        # b.cookies.update({
        #     'ss-id': cookie.strip()
        # })
        p = {
            'Filter': f"substringof('{code.strip()}',Code)"
        }
        res = b.get(f'https://{link}.pos365.vn/api/orders',params=p).json()
        # print(res)
        return res
    except Exception as e:
        return str(e)

@common.route('/Config/VendorSession', methods=['POST'])
def api_VendorSession():
    try:
        cookie = request.form['cookie']
        link = request.form['link']
        b = requests.session()
        b.headers.update({
            'content-type': 'application/json',
            'cookie': f'ss-id={cookie.strip()}'
        })
        # b.cookies.update({
        #     'ss-id': cookie.strip()
        # })
        res = b.get(f'https://{link}.pos365.vn/Config/VendorSession')
        if res.status_code != 200:
            return f'Error {res.status_code}'
        tmp = res.text.split('branch :')
        # print(tmp[1][tmp[1].index(':')+1:])
        current = json.loads(tmp[1].split('}')[0]+'}')
        tmp = res.text.split('branchs:')
        branchs = json.loads(tmp[1].split(']')[0] + ']')
        return jsonify({
            'current': current,
            'branchs': branchs
        })
    except Exception as e:
        # print(e)
        return str(e)
@common.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'GET':
        token = request.args.get('token')
        if token == 'kt365aA@123':
            return render_template('setup.html')
        else:
            return abort(404)
    else:
        token = request.form.get('token')
        if token != 'kt365aA@123':
            return abort(403)
        branch = request.form.get('branch').lower()
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

@common.route('/orders', methods=['POST'])
def orders():
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
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{branch} {now} -> {content}")
        log = Log()
        log.configId = cfg.id
        log.branch = branch
        log.store = store
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
        if content.get('PurchaseDate') is not None and len(str(content.get('PurchaseDate').strip())) == 0:
            raise MissingInformationException('Thiếu thông tin ngày bán (PurchaseDate)')
        if content.get('ReturnDate') is not None and len(str(content.get('ReturnDate').strip())) == 0:
            raise MissingInformationException('Thiếu thông tin ngày bán (ReturnDate)')
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
