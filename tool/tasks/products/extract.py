# import json
# import time
# from concurrent import futures
# from concurrent.futures import wait
# from os.path import dirname
#
# import celery
# import redis
# from celery import Celery
# import multiprocessing as mp
# import warnings
#
# if __name__:
#     import sys
#
#     PATH = dirname(dirname(dirname(__file__)))
#     sys.path.append(PATH)
#     from tool.pos import FullApi
#     from tool.google_sheet import Sheet
#     from tool.pos.product import Product
#     from tool.tasks import make_celery
#
# r = redis.Redis(host='localhost', port=6380)
#
#
# @celery.Task(name='extract_product')
# def extract_product(domain=None, cookie=None, branch=None):
#     global _COUNTER
#     rid = extract_product.request.id
#     print(rid)
#     counter = mp.Value('i', 0)
#     _COUNTER = counter
#     count = 0
#     # time.sleep(3)
#     pub = r.publish(
#         channel=rid,
#         message=json.dumps({'progress': round(float(100 / 100000) * 100, 2), 'status': False})
#     )
#
#     def func(skip, worker):
#         # try:
#         data = []
#         while True:
#             res = api.product_list(skip, worker)
#             if res['status'] == 1:
#                 return data
#             elif res['status'] == 2:
#
#                 with _COUNTER.get_lock():
#                     data.extend(res['result'])
#                     with _COUNTER.get_lock():
#                         _COUNTER.value += len(res['result'])
#                         # print(_COUNTER.value)
#                         r.publish(
#                             channel=rid,
#                             message=json.dumps({
#                                 'progress': f'{_COUNTER.value}/{count}',
#                                 'status': False})
#                         )
#                         # log(rid=rid, state='PROGRESS', info={'current': f'{_COUNTER.value}/{count}'})
#                 skip += 50 * worker
#             # else:
#             #     print(res)
#
#     #
#     api = FullApi(domain, cookie)
#     if not api.switch_branch(branch):
#         return {'status': False}
#     count = api.count_products()
#
#     counter = mp.Value('i', 0)
#     sheet = Sheet()
#     max_workers = 6
#     thread = futures.ThreadPoolExecutor(max_workers=max_workers)
#     tasks = []
#     for i in range(max_workers - 1):
#         # skip = i * 50
#         tasks.append(thread.submit(func, i * 50, max_workers - 1))
#     tasks.append(thread.submit(sheet.create_sheet, domain, 'DS Hàng hoá'))
#     # futures.as_completed(tasks)
#     wait(tasks)
#     r.publish(
#         channel=rid,
#         message=json.dumps({
#             'progress': f'{sheet.sheet_url}',
#             'status': True})
#     )
#     res = []
#     for _ in tasks[:-1]:
#         res.extend(_.result())
#     # log(rid=rid, state='UPLOADING')
#     print('UPLOADING')
#     sheet.insert(data=res)
#     # r.publish(
#     #     channel=rid,
#     #     message=json.dumps({'progress': 'DONE', 'status': False})
#     # )
#     # r.publish(
#     #     channel=rid,
#     #     message=json.dumps({'progress': 'DONE', 'status': True})
#     # )
#     return {'status': True, 'result': 'done'}
