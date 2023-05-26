import json

import jwt
import redis
import requests
from sqlalchemy.sql import null
from flask import Blueprint, request, render_template, jsonify, current_app, session, redirect, Response
from flask_sqlalchemy import SQLAlchemy

from model import TechLog, Log
from role import login_required
from technical_celery import extract_product
from common_celery import convert
from role import login_required
from google.oauth2 import id_token
from google.auth.transport import requests as ggRequests
from flask import current_app

db = SQLAlchemy()
technical = Blueprint('technical', __name__)


@technical.route('/log_tech', methods=['POST'])
def local_technical_log():
    info = request.json.get('info')
    # print(info is None and TechLog.info.default or info
    rid = request.json['rid']
    state = request.json['state']
    l = TechLog.query.filter_by(rid=rid).first()
    if l is not None:
        l.state = state
        l.info = info is not None and info or null()
        try:
            db.session.commit()
        except:
            db.session.rollback()
    return {}


@technical.route('/<id>', methods=['GET'])
def api_task_result(id):
    l = TechLog.query.filter_by(rid=id).first()
    if l is None: return jsonify({'status': 404})
    if l.task_name == 'extract_product':
        task = extract_product.AsyncResult(id)
    else:
        return jsonify({'status': 404})
    print(task.state)
    print(task.info)
    return str(task.state)
    # if task.state == 'PENDING':
    #     response = {
    #         'status': str(task.state)
    #     }
    #     response = Response(json.dumps(response), status=201, mimetype='application/json')
    # elif task.state != 'FAILURE':
    #     response = {
    #         'state': task.state
    #     }
    #     if task.info['status'] is True:
    #         response['state'] = 'SUCCESS'
    #         response['result'] = task.info['result']
    #         response = Response(json.dumps(response), status=200, mimetype='application/json')
    #     else:
    #         response['state'] = 'FAILURE'
    #         response['reason'] = task.info['result']
    #         response = Response(json.dumps(response), status=400, mimetype='application/json')
    #
    # else:
    #     response = {
    #         'state': task.state
    #     }
    #     response = Response(json.dumps(response), status=400, mimetype='application/json')
    # return response


@technical.route('/', methods=['GET'])
def api_technical_department():
    try:
        jwt.decode(request.cookies.get('jwt'), current_app.config['SECRET_KEY'], 'HS256')
        return redirect('/dashboard')
    except:
        return render_template('login.html', gg_client_id=current_app.config['GOOGLE_CLIENT_ID'])

@technical.route('/dashboard', methods=['GET', 'POST'])
@login_required
def api_technical_dashboard():
    return render_template('365.html')


@technical.route('/api/orders', methods=['POST'])
@login_required
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
        res = b.get(f'https://{link}.pos365.vn/api/orders', params=p).json()
        # print(res)
        return res
    except Exception as e:
        return str(e)


@technical.route('/Config/VendorSession', methods=['POST'])
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
        current = json.loads(tmp[1].split('}')[0] + '}')
        tmp = res.text.split('branchs:')
        branch = json.loads(tmp[1].split(']')[0] + ']')
        return jsonify({
            'current': current,
            'branch': branch
        })
    except Exception as e:
        # print(e)
        return Response(str(e), status=400)


@technical.route('/api/extract/products', methods=['POST'])
@login_required
def api_extract_products():
    cookie = request.form['cookie']
    link = request.form['link']
    branch = request.form['branch']
    result = extract_product.delay(domain=link, cookie=cookie, branch=branch)
    l = TechLog()
    l.rid = str(result.id)
    l.task_name = 'extract_product'
    try:
        db.session.add(l)
        db.session.commit()
    except:
        db.session.rollback()
    return f'<a href="/{str(result.id)}">{str(result.id)}</a>'

r = redis.Redis(host="localhost", port=6380)

# @technical.route("/publish/<int:x>/<int:y>")
# def publish_message(x, y):
#     result = add.delay(x, y)
#     r.publish("tasks", result.id)
#     return "Message published!"

# @technical.route('/pub', methods=['GET'])
# def publish_message():
#     print(request.args)
#     message = request.args['message']
#     # Publish the message to the Redis channel
#     r.publish('my_channel', message)
#     return 'Message published successfully'