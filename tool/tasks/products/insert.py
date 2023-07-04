import json
from concurrent import futures
from concurrent.futures import wait
from os.path import dirname
import multiprocessing as mp
import celery
import redis
from celery import Task
from celery import current_app

r = redis.Redis(host='localhost', port=6380)

if __name__:
    import sys

    PATH = dirname(dirname(dirname(dirname(__file__))))
    print(2, PATH)
    sys.path.append(PATH)
    from tool.pos import FullApi
    from tool.google_sheet import Sheet
    from tool.pos.product import Product
    # from tool.tasks.bg import r
    # from tool.tasks.bg import bg
    # from tool.tasks import make_celery
    # from .products import insert
    # from .products import extract
    # from .task2 import task2

#
# class TestCeleryTask(Task,
#                      ):
#     name = 'CeleryTask'
#
#     def run(self):
#         print('abc')
#         print(self.request.id)
#         # print(args)
#         # print(kwargs)
#         # return True


# @current_app.task(name='import_product')
class InsertProduct(Task):
    name = 'InsertProduct'
    # def __init__(self):
    #     self.domain = None
    #     self.cookie = None
    def _thread(self, records, domain, cookie, start, worker, tid):
        index = start

        l = len(records)
        while index < l:
            # print(f'{worker} {index} {l}')
            try:
                data = records[index]
            except Exception as e:
                print(e)
                return
            p = Product(domain, cookie)
            p.setMulCode(data['Mã hàng hóa'])
            stt = p.product_by_code(p.Code)
            # print(f'62 ===> {stt} {p.Code}')
            # if stt['status'] is False:
            #     return
            # else:
            try:
                p.Id = stt['Id']
                p.setName(data['Tên hàng hóa'])
                p.setSerial(data['Quản lý theo Lô Hạn'])
                p.setPrintLabel(data['Không in ra tem nhãn'])
                p.setOpenTopping(data['Mở Extra/Topping khi chọn'])
                p.setHidden(data['Không cho phép bán'])
                p.setVAT(data['VAT'])
                p.setMulPrinter(data['In nhiều vị trí'])
                p.Price = str(data['Giá bán']).strip()
                p.PriceLargeUnit = str(data['Giá bán ĐVT Lớn']).strip()
                p.Cost = str(data['Giá vốn']).strip()

                p.Unit = data['ĐVT'].strip()
                p.LargeUnit = data['ĐVT Lớn'].strip()
                p.LargeUnitCode = data['Mã ĐVT Lớn'].strip()
                p.ConversionValue = data['Giá trị quy đổi']
                p.OrderQuickNotes = data['Ghi chú nhanh khi bán hàng'].strip()
                p.OnHand = data['Tồn kho']
                p.ProductType = data['Loại hàng']
                # print(p.toJson())

                p.Printer = data['Tên máy in']
                p.setMaxQuantity(data['Định mức tồn lớn nhất'])
                p.setMinQuantity(data['Định mức tồn nhỏ nhất'])
                p.setSplitForSalesOrder(data['Tách thành nhiều dòng khi bán hàng'])

                p.setShowBranch(data['Chi nhánh hiển thị'])

                p.setCompositeItemProducts(data['Thành phần'])
                p.setProductAttributes(data['Thuộc tính'])
                p.setImage(data['Hình ảnh'])

                p.setBonus(data['Hoa hồng'])
                p.NCC = data['Mã nhà cung cấp']

                p.setCategory(data['Tên nhóm'])
                # print(p.toJson())
                # print(p.toJson())

                stt = p.product_full_save(p.toJson())
                with _COUNTER.get_lock():
                    _COUNTER.value += 1
                    # print(self.request.id)
                    try:
                        r.publish(
                            channel=tid,
                            message=json.dumps(
                                {
                                    'progress': f'{_COUNTER.value}/{l} {json.dumps(stt)}',
                                    # 'abc': json.dumps(stt),
                                    'status': 0
                                }
                            )
                        )
                    except Exception as e:
                        print(e)

            except Exception as e:
                print(e)
            index += worker
    def run(self, domain=None, cookie=None, branch=None, insert_type=None, data=None):
        global _COUNTER
        _COUNTER = mp.Value('i', 0)
        if insert_type == 1:
            self.domain = domain,
            self.cookie = cookie
            sheet = Sheet()
            sheet.get_sheet_by_link(data)
            records = sheet.extract()
            print(self.request.id)
            # pro = []
            # index = 0
            max_workers = 5
            with futures.ThreadPoolExecutor(max_workers=max_workers) as thread:
                tasks = []
                for i in range(max_workers):
                    # skip = i * 50
                    tasks.append(thread.submit(self._thread, records, domain, cookie, i, max_workers, self.request.id))
                # tasks.append(thread.submit(sheet.create_sheet, domain, 'DS Hàng hoá'))
                futures.as_completed(tasks)
            # wait(tasks)
            print('abc')
            # break
            # p.update({
            #     'Id': id,
            #     'Code': code[0],
            #     'Name': name,
            #     'Unit': data['ĐVT'].strip(),
            #     'LargeUnit': data['ĐVT Lớn'].strip(),
            #     'LargeUnitCode': data['Mã ĐVT Lớn'].strip(),
            #     'ConversionValue': data['Giá trị quy đổi'],
            #     'OrderQuickNotes': data['Ghi chú nhanh khi bán hàng'].strip(),
            #     'Price': data['Giá bán'],
            #     'PriceLargeUnit': data['Giá bán ĐVT Lớn'],
            #     'Cost': data['Giá vốn'],
            #     'IsSerialNumberTracking': serial,
            #     'Printer': data['Tên máy in'].strip()
            # })
            # print(p)

#
# def import_product(domain=None, cookie=None, branch=None, importType=None, data=None):
#     print('xxxxxxx')
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
#                 return
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
