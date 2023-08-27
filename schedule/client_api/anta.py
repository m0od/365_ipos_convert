from datetime import datetime, timedelta

import pymssql
from os.path import dirname


class Anta(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'anta_aeonhd'
        self.ADAPTER_TOKEN = '9a7a4bd5227fdc019d850ebbdda7a98dc5daa8061fdbe1daefc30b6caf341142'
        self.SERVER = '210.245.87.153'
        self.PORT = 1719
        self.USER = '365'
        self.PASS = 'Api@pos2022'
        self.DATABASE = 'AB_Augges'
        self.CONN = None
        self.CURSOR = None
        self.orders = {}
        self.SQL_QUERY = "SELECT TOP 10000 dbo.SlBlM.ID AS order_code, dbo.SlBlM.InsertDate AS pur_date, dbo.SlBlM.Tien_GtGt as vat," \
                         "dbo.SlBlM.Tien_Hang AS total, dbo.DmH.Ma_Hang AS product_code, dbo.DmH.Ten_Hang AS name," \
                         "dbo.SlBlD.Don_Gia AS price, dbo.SlBlD.So_Luong AS qty, dbo.SlBlD.Tien_CK + dbo.SlBlD.Tien_Giam AS discount," \
                         "dbo.dmnx.Ma_Nx as payment_method " \
                         "FROM dbo.SlBlD " \
                         "LEFT JOIN dbo.SlBlM ON dbo.SlBlD.ID = dbo.SlBlM.ID " \
                         "LEFT JOIN dbo.DmH ON dbo.SlBlD.ID_Hang = dbo.DmH.ID " \
                         "LEFT JOIN dbo.DmDvt ON dbo.DmH.ID_DvCs = dbo.DmDvt.ID " \
                         "LEFT JOIN dbo.DmNx ON dbo.SlBlM.ID_Nx = dbo.DmNx.ID " \
                         "WHERE dbo.SlBlD.ID_Hang IS NOT NULL AND dbo.SlBlM.SNgay='{}' " \
                         "AND ISNULL(dbo.SlBlD.ID_Kho, dbo.SlBlM.ID_Kho) = 166 " \
                         "ORDER BY dbo.SlBlM.ID"
        self.METHOD = {
            'VISATTT_A': 'THẺ',
            'TM.TNHA_AN': 'CASH',
            'TM_TNHA(VE.CTY)': 'CASH'
        }

    def login(self):
        try:
            self.CONN = pymssql.connect(server=self.SERVER, port=self.PORT,
                                        user=self.USER, password=self.PASS,
                                        database=self.DATABASE)
            self.CURSOR = self.CONN.cursor(as_dict=True)
            return True
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[MSSQL Error] {str(e)}')
            return False

    def get_data(self, date_from):
        cv = Converter()
        self.orders = {}
        if not self.login(): return False
        try:
            self.CURSOR.execute(self.SQL_QUERY.format(date_from.strftime('%y%m%d')))
            row = self.CURSOR.fetchone()
            while row:
                order_code = str(row['order_code']).strip()
                pm = row['payment_method'].strip()
                if self.METHOD.get(pm) is not None:
                    pm = self.METHOD.get(pm)
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
                    # print('update', type(json.loads(self.orders[order_code].get('od'))))
                    od = self.orders[order_code].get('OrderDetails')
                    # print(od)
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
                # print(orders.get(order_code))
                row = self.CURSOR.fetchone()
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Fetch Data] {str(e)}')
            pass
        self.CONN.close()
        for _, js in self.orders.items():
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=js)


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order
    from schedule.client_api.font_vi import Converter

    # now = datetime.now()
    # Anta().get_data(now - timedelta(days=1))