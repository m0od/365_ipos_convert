import json
import time
from concurrent import futures
from concurrent.futures import wait
from os.path import dirname

import redis
from celery import Celery
import multiprocessing as mp
import warnings



# from tool.tasks.demo import make_celery

if __name__:
    import sys

    PATH = dirname(dirname(dirname(__file__)))
    sys.path.append(PATH)
    from tool.pos import FullApi
    from tool.google_sheet import Sheet
    from tool.pos.product import Product
    from tool.tasks import make_celery
    from .products import insert
    from .products import extract
    from .products.insert import InsertProduct
    # from .task2 import task2

# __all__ = ['insert']

warnings.filterwarnings('ignore')
CELERY_BROKER_URL = 'redis://localhost:6380'
RESULT_BACKEND = 'redis://localhost:6380'
r = redis.Redis(host='localhost', port=6380)
# pubsub = redis_client.pubsub()
# pubsub.subscribe('my_channel')

# bg = Celery('kt365', backend=RESULT_BACKEND, broker=CELERY_BROKER_URL)
bg = make_celery()
insert_product = bg.register_task(InsertProduct())
# @bg.task(name='xxx', base=CustomTask)
# def xxx(self):
#     print('running')
# bg.autodiscover_tasks()
# bg.autodiscover_tasks(['products'], related_name='insert', force=True)
# bg.register_task(insert.ImportProducts)
@bg.task(name='extract_product')
def extract_product(domain=None, cookie=None, branch=None):
    global _COUNTER
    rid = extract_product.request.id
    print(rid)
    counter = mp.Value('i', 0)
    _COUNTER = counter
    count = 0
    # time.sleep(3)
    # pub = r.publish(
    #     channel=rid,
    #     message=json.dumps({'progress': round(float(100 / 100000) * 100, 2), 'status': False})
    # )

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
                        # print(_COUNTER.value)
                        r.publish(
                            channel=rid,
                            message=json.dumps({
                                'progress': f'{_COUNTER.value}/{count}',
                                'status': False})
                        )
                        # log(rid=rid, state='PROGRESS', info={'current': f'{_COUNTER.value}/{count}'})
                skip += 50 * worker
            # else:
            #     print(res)

    #
    api = FullApi(domain, cookie)
    if not api.switch_branch(branch):
        return {'status': False}
    count = api.count_products()

    counter = mp.Value('i', 0)
    sheet = Sheet()
    max_workers = 6
    thread = futures.ThreadPoolExecutor(max_workers=max_workers)
    tasks = []
    for i in range(max_workers - 1):
        # skip = i * 50
        tasks.append(thread.submit(func, i * 50, max_workers - 1))
    tasks.append(thread.submit(sheet.create_sheet, domain, 'DS Hàng hoá'))
    # futures.as_completed(tasks)
    wait(tasks)
    r.publish(
        channel=rid,
        message=json.dumps({
            'progress': f'{sheet.sheet_url}',
            'status': True})
    )
    res = []
    for _ in tasks[:-1]:
        res.extend(_.result())
    # log(rid=rid, state='UPLOADING')
    print('UPLOADING')
    sheet.insert(data=res)
    # r.publish(
    #     channel=rid,
    #     message=json.dumps({'progress': 'DONE', 'status': False})
    # )
    # r.publish(
    #     channel=rid,
    #     message=json.dumps({'progress': 'DONE', 'status': True})
    # )
    return {'status': True, 'result': 'done'}


# @bg.task(name='import_product')
# def import_product(domain=None, cookie=None, branch=None, importType=None, data=None):
#     global _COUNTER
#     if importType == 1:
#         sheet = Sheet()
#         sheet.get_sheet_by_link(data)
#         records = sheet.extract(domain, cookie, branch)
#         for data in records:
#             p = Product(domain, cookie)
#             p.setMulCode(data['Mã hàng hóa'])
#             stt = p.product_by_code(p.Code)
#             if stt['status'] is False:
#
#             p.setName(data['Tên hàng hóa'])
#             p.setSerial(data['Quản lý theo Lô Hạn'])
#             p.setPrintLabel(data['Không in ra tem nhãn'])
#             p.setOpenTopping(data['Mở Extra/Topping khi chọn'])
#             p.setHidden(data['Không cho phép bán'])
#             p.setVAT(data['VAT'])
#             p.setMulPrinter(data['In nhiều vị trí'])
#             p.Price = str(data['Giá bán']).strip()
#             p.PriceLargeUnit = str(data['Giá bán ĐVT Lớn']).strip()
#             p.Cost = str(data['Giá vốn']).strip()
#             p.Unit = data['ĐVT'].strip()
#             p.LargeUnit = data['ĐVT Lớn'].strip()
#             p.LargeUnitCode = data['Mã ĐVT Lớn'].strip()
#             p.ConversionValue = data['Giá trị quy đổi']
#             p.OrderQuickNotes = data['Ghi chú nhanh khi bán hàng'].strip()
#             p.OnHand = data['Tồn kho']
#             p.ProductType = data['Loại hàng']
#             p.CategoryName = data['Tên nhóm']
#             p.Printer = data['Tên máy in']
#             p.setMaxQuantity(data['Định mức tồn lớn nhất'])
#             p.setMinQuantity(data['Định mức tồn nhỏ nhất'])
#             p.setSplitForSalesOrder(data['Tách thành nhiều dòng khi bán hàng'])
#             p.setShowBranch(data['Chi nhánh hiển thị'])
#             p.setCompositeItemProducts(data['Thành phần'])
#             p.setProductAttributes(data['Thuộc tính'])
#             p.setImage(data['Hình ảnh'])
#             p.setBonus(data['Hoa hồng'])
#             p.toJson()
#             # break
#             # p.update({
#             #     'Id': id,
#             #     'Code': code[0],
#             #     'Name': name,
#             #     'Unit': data['ĐVT'].strip(),
#             #     'LargeUnit': data['ĐVT Lớn'].strip(),
#             #     'LargeUnitCode': data['Mã ĐVT Lớn'].strip(),
#             #     'ConversionValue': data['Giá trị quy đổi'],
#             #     'OrderQuickNotes': data['Ghi chú nhanh khi bán hàng'].strip(),
#             #     'Price': data['Giá bán'],
#             #     'PriceLargeUnit': data['Giá bán ĐVT Lớn'],
#             #     'Cost': data['Giá vốn'],
#             #     'IsSerialNumberTracking': serial,
#             #     'Printer': data['Tên máy in'].strip()
#             # })
#             print(p)
