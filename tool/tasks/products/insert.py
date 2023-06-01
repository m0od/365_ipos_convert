from os.path import dirname

import celery
from celery import Task
from celery import current_app

if __name__:
    import sys

    PATH = dirname(dirname(dirname(dirname(__file__))))
    print(2, PATH)
    sys.path.append(PATH)
    from tool.pos import FullApi
    from tool.google_sheet import Sheet
    from tool.pos.product import Product
    # from tool.tasks.bg import bg
    # from tool.tasks import make_celery
    # from .products import insert
    # from .products import extract
    # from .task2 import task2

class TestCeleryTask(Task,
):
    name = 'CeleryTask'
    def run(self):
        print('abc')
        print(self.request.id)
        # print(args)
        # print(kwargs)
        # return True


@current_app.task(name='import_product')
def import_product(domain=None, cookie=None, branch=None, importType=None, data=None):
    print('xxxxxxx')
    global _COUNTER
    if importType == 1:
        sheet = Sheet()
        sheet.get_sheet_by_link(data)
        records = sheet.extract(domain, cookie, branch)
        for data in records:
            p = Product(domain, cookie)
            p.setMulCode(data['Mã hàng hóa'])
            stt = p.product_by_code(p.Code)
            if stt['status'] is False:
                return

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
            p.CategoryName = data['Tên nhóm']
            p.Printer = data['Tên máy in']
            p.setMaxQuantity(data['Định mức tồn lớn nhất'])
            p.setMinQuantity(data['Định mức tồn nhỏ nhất'])
            p.setSplitForSalesOrder(data['Tách thành nhiều dòng khi bán hàng'])
            p.setShowBranch(data['Chi nhánh hiển thị'])
            p.setCompositeItemProducts(data['Thành phần'])
            p.setProductAttributes(data['Thuộc tính'])
            p.setImage(data['Hình ảnh'])
            p.setBonus(data['Hoa hồng'])
            p.toJson()
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
            print(p)
