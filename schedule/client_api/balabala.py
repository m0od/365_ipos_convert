from datetime import datetime, timedelta

import pymssql
from os.path import dirname


class Balabala(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'balabala_aeonhd'
        self.ADAPTER_TOKEN = '2f8ffa1128747fc4b7614d9fce23ef5226dd9e3c9be7bd390c957af818bac746'
        self.SERVER = '210.245.87.153'
        self.PORT = 1719
        self.USER = '365'
        self.PASS = 'Api@pos2022'
        self.DATABASE = 'SG_Augges'
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
                         "AND ISNULL(dbo.SlBlD.ID_Kho, dbo.SlBlM.ID_Kho) = 61 " \
                         "ORDER BY dbo.SlBlM.ID"
        self.METHOD = {
            '2-TOS.THE.BA': 'THẺ',
            '1-TOS.TM.BA': 'CASH'
        }

    def login(self):
        try:
            self.CONN = pymssql.connect(server=self.SERVER, port=self.PORT,
                                        user=self.USER, password=self.PASS,
                                        database=self.DATABASE)
            self.CURSOR = self.CONN.cursor(as_dict=True)
            return True
        except Exception as e:
            print(e)
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[MSSQL Error] {str(e)}')
            return False

    def get_data(self, date_from):
        cv = Converter()
        self.orders = {}
        if not self.login(): return False
        try:
            print(self.SQL_QUERY.format(date_from.strftime('%y%m%d')))
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
            print(js)
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=js)

        # return True
    # def pm(self):
    #     browser = auth('am069', 'admin', '123456')
    #     self.cursor.execute('select * from dbo.dmnx')
    #     row = self.cursor.fetchone()
    #     while row:
    #         # print(row['Ma_Nx'])
    #         id = api_accounts.put_payment_method(browser, 'am069', f"{row['Ma_Nx'].strip()}")
    #         print(f"'{row['Ma_Nx'].strip()}': {id}")
    #         row = self.cursor.fetchone()


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order
    from schedule.client_api.font_vi import Converter
    # now = datetime.now()
    # Balabala().get_data(now - timedelta(days=1))
