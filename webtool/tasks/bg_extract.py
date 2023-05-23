import json
import time
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
# from ggsheet.sheet_api import Sheet
# from pos365api import API
# from threading import current_thread
import warnings

warnings.filterwarnings('ignore')
CELERY_BROKER_URL = 'redis://localhost:6379'
RESULT_BACKEND = 'redis://localhost:6379'
r = redis.Redis(host='localhost', port=6379)
# pubsub = redis_client.pubsub()
# pubsub.subscribe('my_channel')

bg = Celery('kt365', backend=RESULT_BACKEND, broker=CELERY_BROKER_URL)
@bg.task(name='abc')
def abc(txt):
    for i in range(100001):
        pub = r.publish(
            channel=abc.request.id,
            message=json.dumps({'progress':round(float(i/100000)*100,2), 'status':False})
        )
        # time.sleep(1)
    pub = r.publish(
        channel=abc.request.id,
        message=json.dumps({'status':True})
    )
    print('process_message')
    # Process the message
    print(f'Received message: {txt}')