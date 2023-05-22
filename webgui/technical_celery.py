import json
from concurrent import futures
from concurrent.futures import wait
from datetime import datetime
from threading import Lock

import redis
import requests
from celery import Celery
# from celery import Celery
from pytz import timezone
import multiprocessing as mp
from ggsheet.sheet_api import Sheet
from pos365api import API
from threading import current_thread
import warnings

warnings.filterwarnings('ignore')
LOCAL_URL = 'https://adapter.pos365.vn'
CELERY_BROKER_URL = 'redis://localhost:6380'
RESULT_BACKEND = 'redis://localhost:6380'
redis_client = redis.Redis(host='localhost', port=6380)
# pubsub = redis_client.pubsub()
# pubsub.subscribe('my_channel')

background = Celery('Backend kt365', backend=RESULT_BACKEND, broker=CELERY_BROKER_URL)
# @background.task
# def process_message(message):
#     print('process_message')
#     # Process the message
#     print(f'Received message: {message}')
#
# def handle_message():
#     pubsub = redis_client.pubsub()
#     pubsub.subscribe('my_channel')
#     for message in pubsub.listen():
#         print(message)
#         if message['type'] == 'message':
#             message_data = message['data'].decode('utf-8')
#             process_message.delay(message_data)

# handle_message()


@background.task(bind=True)
def extract_product(self, domain=None, cookie=None, branch=None):
    global _COUNTER
    rid = self.request.id
    counter = mp.Value('i', 0)
    _COUNTER = counter
    count = 0

    def func(skip, worker):
        # try:
        data = []
        while True:
            res = api.product_list(skip, worker)
            if res['status'] == 1:
                return data
            elif res['status'] == 2:

                with _COUNTER.get_lock():
                    data.extend(res['result'])
                    with _COUNTER.get_lock():
                        _COUNTER.value += len(res['result'])
                        log(rid=rid, state='PROGRESS', info={'current': f'{_COUNTER.value}/{count}'})
                skip += 50 * worker

    api = API(domain, cookie)
    if not api.switch_branch(branch):
        return {'status': False}
    count = api.count_products()

    counter = mp.Value('i', 0)
    sheet = Sheet()
    max_workers = 6
    thread = futures.ThreadPoolExecutor(max_workers=max_workers)
    tasks = []
    for i in range(max_workers - 1):
        skip = i * 50
        tasks.append(thread.submit(func, i * 50, max_workers))
    tasks.append(thread.submit(sheet.create_sheet, domain, 'DS Hàng hoá'))
    # futures.as_completed(tasks)
    wait(tasks)
    print('DONE')
    res = []
    for _ in tasks[:-1]:
        res.extend(_.result())
    log(rid=rid, state='UPLOADING')
    print('UPLOADING')
    sheet.insert(data=res)
    log(rid=rid, state='SUCCESS', info={'sheet': sheet.sheet_id})
    return {'status': True, 'result': 'done'}

# @background.task
# def add(x, y):
#     return x + y
def log(rid=None, state=None, info=None):
    try:
        js = {'rid': rid, 'state': state, 'info': info}
        # if info is not None:
        #     js.update({'info': info})
        requests.post(f'http://127.0.0.1:6060/log_tech', json=js, verify=False)
        # requests.post(f'http://adapter.pos365.vn:6000/log', json={'rid': id, 'result': str(result)})
    except Exception as e:
        print(e)
        pass
