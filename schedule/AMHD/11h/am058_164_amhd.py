import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname
import xml.etree.cElementTree as ET
from unidecode import unidecode


class AM058(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'forever_amhd'
        self.ADAPTER_TOKEN = '1b531fbaae1937206555c47223568dc7b1fa4b165c80aff7c4a8bdc55d12afd6'
        self.FOLDER = '164_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%m%Y')
        self.EXT = f'*.xml'
        # self.METHOD = {
        #     'CASH': 'CASH',
        #     'MASTERCARD': 'THẺ',
        #     'VISA': 'THẺ',
        #     'LOCAL BANK': 'BANK'
        # }

    def scan_file(self):
        try:
            return glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            # return max(files, key=os.path.getmtime)
            # idx = _.rindex('/')
            # name = _[idx + 1:]
            # idx = name.rindex('.')
            # name = name[:idx]
            # t = os.path.getmtime(_)
            # t = datetime.fromtimestamp(t).strftime('%Y%m%d %H:%M:%S')
            # os.rename(_, f'{self.FULL_PATH}/{name}_{t}.xls')
            # return f'{self.FULL_PATH}/{name}_{t}.xls'
        except:
            return None

    def get_data(self):
        def get_value(node):
            try:
                return float(node)
            except:
                return 0

        from pos_api.adapter import submit_order, submit_payment, submit_error
        files = self.scan_file()
        # print(files)
        if not len(files):
            submit_error(self.ADAPTER_RETAILER, 'SUMMARY NOT FOUND')
            return
        # print(DATA)
        for DATA in files:
            print(DATA)

            ns = {"doc": "urn:schemas-microsoft-com:office:spreadsheet"}

            tree = ET.parse(DATA)
            root = tree.getroot()

            # def main():
            #     """ main """
            parsed_xml = tree

            data = []
            headers = []
            for i, node in enumerate(root.findall('.//doc:Row', ns)):
                if i < 4: continue
                # node.find(f'doc:Cell[1]/doc:Data', ns)
                # data.append({
                #     'account': getvalueofnode(node.find('doc:Cell[1]/doc:Data', ns)),
                #     'total': getvalueofnode(node.find('doc:Cell[2]/doc:Data', ns))
                # })
                cols = node.findall('.//doc:Cell/doc:Data', ns)
                pur_date = cols[0].text
                if i == 4:
                    # print(type(cols), len(cols))
                    for _ in cols:
                        # print(_.text)
                        headers.append(unidecode(_.text).upper())
                else:
                    tmp = {}
                    for j, _ in enumerate(cols):
                        tmp.update({headers[j]: _.text})
                    data.append(tmp)
            # print(data[0])
            orders = {}
            for _ in data:
                try:
                    code = _['SO CT']
                    pur_date = datetime.strptime(_['NGAY CT'], '%Y-%m-%d')
                    p_code = _['MA MAT HANG']
                    p_name = _['TEN MAT HANG']
                    qty = get_value(_['SO LUONG'])
                    price = get_value(_['DON GIA'])
                    discount = get_value(_['CK DUOC HUONG'])
                    total = get_value(_['TT SAU CK'])
                    # print(qty, price, discount, total)
                    if not orders.get(code):
                        orders.update({code: {
                            'Code': code,
                            'Status': 2,
                            'PurchaseDate': pur_date.strftime('%Y-%m-%d 07:00:00'),
                            'Total': total,
                            'TotalPayment': total,
                            'VAT': 0,
                            'Discount': discount,
                            'OrderDetails': [{
                                'Code': p_code,
                                'Name': p_name.strip(),
                                'Price': price,
                                'Quantity': qty
                            }],
                            'PaymentMethods': [{'Name': 'CASH', 'Value': total}]
                        }})
                    else:
                        orders[code]['Total'] += total
                        orders[code]['TotalPayment'] += total
                        orders[code]['Discount'] += discount
                        orders[code]['PaymentMethods'] = [
                            {'Name': 'CASH',
                             'Value': orders[code]['Total']}
                        ]
                        orders[code]['OrderDetails'].append({
                            'Code': p_code,
                            'Name': p_name.strip(),
                            'Price': price,
                            'Quantity': qty
                        })
                except:
                    pass
            for _, order in orders.items():
                # print(order)
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
            self.backup(DATA)

    def backup(self, DATA):
        idx = DATA.rindex('/')
        name = DATA[idx + 1:]
        if os.path.exists(f'{self.FULL_PATH}/bak/{name}'):
            os.remove(f'{self.FULL_PATH}/bak/{name}')
        try:
            os.mkdir(f'{self.FULL_PATH}/bak')
        except:
            pass
        try:
            shutil.move(DATA, f'{self.FULL_PATH}/bak')
        except:
            pass
