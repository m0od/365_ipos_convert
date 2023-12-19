import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname


class AM035(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from drive import Google
        self.ADAPTER_RETAILER = 'khaolao_amhd'
        self.ADAPTER_TOKEN = '529f37924b9bae0eded85c3ef353ea5fa206d309a50b7b2bedece24cccd49765'
        self.FOLDER = '129_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*.xlsx'
        self.GG = Google()
        self.GG.FOLDER_ID = '1MncWjpNNpQ7WBbw1Itmm1zMqWZ3ixHvu'

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

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

    def extract_data(self, SHEET_ID):
        # print(SHEET_ID)
        from pos_api.adapter import submit_order
        ws = self.GG.SHEETS.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range='1:1000'
        ).execute()
        count = 0
        for row, rec in enumerate(ws['values'][2:-2]):
            try:
                code = rec[7].strip()
                pur_date = f'{rec[5].strip()} {rec[13].strip()}'
                pur_date = datetime.strptime(pur_date, '%d/%m/%Y %H:%M')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                total = float(rec[19].replace('.00', '').replace(',', ''))
                discount = abs(float(rec[15].replace('.00', '').replace(',', '')))
                # discount += float(rec[26].replace('.00', '').replace(',', ''))
                vat = float(rec[17].replace('.00', '').replace(',', ''))
                pms = []
                cash = float(rec[20].replace('.00', '').replace(',', ''))
                credit_card = float(rec[21].replace('.00', '').replace(',', ''))
                redplus = float(rec[22].replace('.00', '').replace(',', ''))
                voucher = float(rec[23].replace('.00', '').replace(',', ''))
                vnpay = float(rec[24].replace('.00', '').replace(',', ''))
                qr_ha_dong = float(rec[25].replace('.00', '').replace(',', ''))
                zalopay = float(rec[26].replace('.00', '').replace(',', ''))
                momo = float(rec[27].replace('.00', '').replace(',', ''))
                now = float(rec[28].replace('.00', '').replace(',', ''))
                baemin = float(rec[29].replace('.00', '').replace(',', ''))
                clingme = float(rec[30].replace('.00', '').replace(',', ''))
                vinid = float(rec[31].replace('.00', '').replace(',', ''))
                customer = float(rec[32].replace('.00', '').replace(',', ''))
                paylater = float(rec[33].replace('.00', '').replace(',', ''))
                debit_card = float(rec[34].replace('.00', '').replace(',', ''))
                vib_cong_no = float(rec[35].replace('.00', '').replace(',', ''))
                momo_cong_no = float(rec[36].replace('.00', '').replace(',', ''))
                qr_thanh_xuan = float(rec[37].replace('.00', '').replace(',', ''))
                qr_viettin = float(rec[38].replace('.00', '').replace(',', ''))
                other = float(rec[39].replace('.00', '').replace(',', ''))
                pms = [
                    {'Name': 'CASH', 'Value': cash},
                    {'Name': 'CREDIT CARD', 'Value': credit_card},
                    {'Name': 'REDPLUS', 'Value': redplus},
                    {'Name': 'VOUCHER', 'Value': voucher},
                    {'Name': 'VNPAY', 'Value': vnpay},
                    {'Name': 'QRPAY HÀ ĐÔNG', 'Value': qr_ha_dong},
                    {'Name': 'ZALOPAY', 'Value': zalopay},
                    {'Name': 'MOMO', 'Value': momo},
                    {'Name': 'NOW', 'Value': now},
                    {'Name': 'BAEMIN', 'Value': baemin},
                    {'Name': 'CLINGME', 'Value': clingme},
                    {'Name': 'VINID', 'Value': vinid},
                    {'Name': 'CUSTOMER DEPOSIT', 'Value': customer},
                    {'Name': 'PAY LATER', 'Value': paylater},
                    {'Name': 'DEBIT CARD', 'Value': debit_card},
                    {'Name': 'VIB CÔNG NỢ', 'Value': vib_cong_no},
                    {'Name': 'MOMO CÔNG NỢ', 'Value': momo_cong_no},
                    {'Name': 'QRCODE THANH XUÂN', 'Value': qr_thanh_xuan},
                    {'Name': 'QR VIETTIN', 'Value': qr_viettin},
                    {'Name': 'OTHER', 'Value': other},
                ]
                for idx, _ in enumerate(pms.copy()):
                    if _['Value'] == 0: pms.remove(_)
                # print(pms)
                order = {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date,
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': vat,
                    'Discount': discount,
                    'OrderDetails': [{'ProductId': 0}],
                    'PaymentMethods': pms
                }
                # print(order)
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=order)
                count += 1
            except:
                pass
        self.GG.delete(SHEET_ID)
        # if count == 0:
        #     self.send_zero()

    def get_data(self):
        from pos_api.adapter import submit_error
        DATA = self.scan_file()
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        try:
            self.GG.google_auth()
            SHEET_ID = self.GG.create_sheet(DATA)
            self.extract_data(SHEET_ID)
            self.backup(DATA)
        except Exception as e:
            submit_error(self.ADAPTER_RETAILER, reason=str(e))

    def send_zero(self):
        from pos_api.adapter import submit_order
        order = {
            'Code': f'NOBILL_{self.DATE.strftime("%d%m%Y")}',
            'Status': 2,
            'PurchaseDate': self.DATE.strftime('%Y-%m-%d 07:00:00'),
            'Total': 0,
            'TotalPayment': 0,
            'VAT': 0,
            'Discount': 0,
            'OrderDetails': [{'ProductId': 0}],
            'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
        }
        submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)