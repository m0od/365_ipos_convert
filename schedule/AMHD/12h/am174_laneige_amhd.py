import sys
from datetime import datetime, timedelta
from os.path import dirname

class AM174(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from drive import Google
        self.ADAPTER_RETAILER = 'laneige_amhd'
        self.ADAPTER_TOKEN = '847d18ced3ad93f957199727f626e22e14ffd9a9a8a0a41a7ab911a862184176'
        self.GG = Google()
        self.SHEET_ID = '1-VOAOgCVfHARl2riwwIBCr1eYXGKNb54O8SePm2DDgY'

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        self.GG.google_auth()
        ord = []
        try:
            ws = self.GG.SHEETS.spreadsheets().values().get(
                spreadsheetId=self.SHEET_ID,
                range='1:1000'
            ).execute()
            raw = ws['values']
            header = raw[0]
            for row, _ in enumerate(raw[2:]):
                try:
                    rec = dict(zip(header, _))
                    if rec.get('Done'): continue
                    pms = []
                    try:
                        date = rec['Ngày'].strip()
                    except:
                        continue
                    if not len(date): continue
                    try:
                        pur_date = datetime.strptime(date, '%d/%m/%Y')
                        pur_date = pur_date + timedelta(hours=10)
                    except:
                        continue
                    code = pur_date.strftime("%Y%m%d")
                    total = float(rec['Tổng doanh số'].split()[0].replace(',', ''))
                    try:
                        vat = float(rec['Thuế'].split()[0].replace(',', ''))
                    except:
                        vat = 0
                    try:
                        cash = float(rec['Doanh số tiền mặt'].split()[0].replace(',', ''))
                    except:
                        cash = 0
                    try:
                        card = float(rec['Doanh số thẻ'].split()[0].replace(',', ''))
                    except:
                        card = 0
                    try:
                        other = float(rec['Doanh số khác'].split()[0].replace(',', ''))
                    except:
                        other = 0
                    if cash != 0:
                        pms.append({'Name': 'CASH', 'Value': cash})
                    if card != 0:
                        pms.append({'Name': 'CARD', 'Value': card})
                    if other != 0:
                        pms.append({'Name': 'OTHER', 'Value': other})
                    count = int(rec['Số đơn hàng'])
                    for i in range(1, count):
                        ord.append({
                            'Code': f'{code}_{i}',
                            'Status': 2,
                            'PurchaseDate': pur_date,
                            'Total': 0,
                            'TotalPayment': 0,
                            'VAT': 0,
                            'Discount': 0,
                            'PaymentMethods': [{'Name': 'CASH', 'Value': 0}],
                            'OrderDetails': []
                        })
                    ord.append({
                        'Code': f'{code}_{count}',
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': vat,
                        'Discount': 0,
                        'PaymentMethods': pms,
                        'OrderDetails': []
                    })
                    if len(ord) > 0:
                        self.GG.SHEETS.spreadsheets().values().update(
                            spreadsheetId=self.SHEET_ID,
                            range=f'I{row + 3}',
                            valueInputOption='USER_ENTERED',
                            body={
                                'values': [[datetime.now().strftime('%y-%m-%d %H:%M:%S')]]
                            },
                        ).execute()
                except Exception as e:
                    submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        total_bill = len(ord)
        for i in range(len(ord)):
            pur_date = ord[i]['PurchaseDate']
            pur_date = pur_date + timedelta(seconds=i * int(43200 / total_bill))
            ord[i]['PurchaseDate'] = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=ord[i])

