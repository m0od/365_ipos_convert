from datetime import datetime, timedelta
import sys
import pymssql
from os.path import dirname


class AM101(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'antakids_amhd'
        self.ADAPTER_TOKEN = 'b6db143de22be38121ad6f51a9f26ee56fde4b713c95b98a1eba49dafd310341'
        self.SERVER = '210.245.87.153'
        self.PORT = 1719
        self.USER = '365'
        self.PASS = 'Api@pos2022'
        self.DATABASE = 'AB_Augges'
        self.CONN = None
        self.CURSOR = None
        self.orders = {}
        self.DATE = datetime.now() - timedelta(days=1)
        self.QUERY = None

    def login(self):
        from pos_api.adapter import submit_error
        try:
            self.CONN = pymssql.connect(server=self.SERVER, port=self.PORT,
                                        user=self.USER, password=self.PASS,
                                        database=self.DATABASE)
            self.CURSOR = self.CONN.cursor(as_dict=True)
            return True
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[MSSQL Error] {str(e)}')
            return False

    def set_query(self):
        self.QUERY = ['SELECT', 'TOP', '10000', 'dbo.SlBlM.ID', 'AS', 'order_code', ',']
        self.QUERY += ['dbo.SlBlM.InsertDate', 'AS', 'pur_date', ',']
        self.QUERY += ['dbo.SlBlM.Tien_GtGt', 'AS', 'vat', ',']
        self.QUERY += ['dbo.SlBlM.Tien_Hang', 'AS', 'total', ',']
        self.QUERY += ['dbo.DmH.Ma_Hang', 'AS', 'product_code', ',']
        self.QUERY += ['dbo.DmH.Ten_Hang', 'AS', 'name', ',']
        self.QUERY += ['dbo.SlBlD.Don_Gia', 'AS', 'price', ',']
        self.QUERY += ['dbo.SlBlD.So_Luong', 'AS', 'qty', ',']
        self.QUERY += ['dbo.SlBlD.Tien_CK', '+', 'dbo.SlBlD.Tien_Giam', 'AS', 'discount', ',']
        self.QUERY += ['dbo.dmnx.Ma_Nx', 'AS', 'payment_method']
        self.QUERY += ['FROM', 'dbo.SlBlD']
        self.QUERY += ['LEFT', 'JOIN', 'dbo.SlBlM']
        self.QUERY += ['ON', 'dbo.SlBlD.ID', '=', 'dbo.SlBlM.ID']
        self.QUERY += ['LEFT', 'JOIN', 'dbo.DmH']
        self.QUERY += ['ON', 'dbo.SlBlD.ID_Hang', '=', 'dbo.DmH.ID']
        self.QUERY += ['LEFT', 'JOIN', 'dbo.DmDvt']
        self.QUERY += ['ON', 'dbo.DmH.ID_DvCs', '=', 'dbo.DmDvt.ID']
        self.QUERY += ['LEFT', 'JOIN', 'dbo.DmNx']
        self.QUERY += ['ON', 'dbo.SlBlM.ID_Nx', '=', 'dbo.DmNx.ID']
        self.QUERY += ['WHERE', 'dbo.SlBlD.ID_Hang', 'IS', 'NOT', 'NULL']
        self.QUERY += ['AND', 'dbo.SlBlM.SNgay', '=', f"'{self.DATE.strftime('%y%m%d')}'"]
        self.QUERY += ['AND', 'ISNULL', '(', 'dbo.SlBlD.ID_Kho', ',', 'dbo.SlBlM.ID_Kho', ')']
        self.QUERY += ['=', '169']
        self.QUERY += ['ORDER', 'BY', 'dbo.SlBlM.ID']

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        from font_vi import Converter
        cv = Converter()
        self.set_query()
        self.orders = {}
        if not self.login(): return False
        try:
            self.CURSOR.execute(' '.join(self.QUERY))
            row = self.CURSOR.fetchone()
            while row:
                order_code = str(row['order_code']).strip()
                pm = row['payment_method'].strip()
                if self.orders.get(order_code) is None:
                    total = int(row['total']) - int(row['discount'])
                    self.orders.update({
                        order_code: {
                            'Code': order_code,
                            'Status': 2,
                            'PurchaseDate': row['pur_date'].strftime('%Y-%m-%d %H:%M:%S'),
                            'Total': total,
                            'TotalPayment': total,
                            'VAT': 0,
                            'Discount': int(row['discount']),
                            'OrderDetails': [{
                                'Code': row['product_code'].strip(),
                                'Name': cv.convert(ori=row['name'].strip()),
                                'Price': int(row['price']),
                                'Quantity': int(row['qty'])
                            }],
                            'PaymentMethods': [
                                {
                                    'Name': pm,
                                    'Value': total
                                }
                            ]
                        }
                    })
                else:
                    total = self.orders[order_code]['Total'] - int(row['discount'])
                    od = self.orders[order_code].get('OrderDetails')
                    od.append({
                        'Code': row['product_code'].strip(),
                        'Name': cv.convert(ori=row['name'].strip()),
                        'Price': int(row['price']),
                        'Quantity': int(row['qty'])
                    })
                    self.orders[order_code].update({
                        'Discount': self.orders[order_code]['Discount'] + int(row['discount']),
                        'OrderDetails': od,
                        'Total': total,
                        'TotalPayment': total,
                        'PaymentMethods': [
                            {
                                'Name': pm,
                                'Value': total
                            }
                        ]
                    })
                row = self.CURSOR.fetchone()
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Fetch Data] {str(e)}')
            pass
        self.CONN.close()
        for _, js in self.orders.items():
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=js)


# _ = AM101()
# idx = 1
# while True:
#     _.DATE = datetime.strptime('20230101', '%Y%m%d') - timedelta(days=idx)
#     if _.DATE.strftime('%Y%m%d') == '20211231':
#         break
#     _.get_data()
#     idx += 1
