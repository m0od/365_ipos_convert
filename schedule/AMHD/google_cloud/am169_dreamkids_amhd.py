import sys
from datetime import datetime
from os.path import dirname

class AM169(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from drive import Google
        self.ADAPTER_RETAILER = 'dreamkids_amhd'
        self.ADAPTER_TOKEN = 'ff1d7b570e33a053cffe09ea00365d25ac5baa0652c783cf2f35bbd47f87b130'
        self.GG = Google()
        self.SHEET_ID = '194j9p4EOevSlkasJlqxfN6DXj5e9Ixk2Au0q1h8l8fI'

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
            for row, _ in enumerate(raw[1:]):
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
                        pur_date = datetime.strptime(date, '%d-%m-%Y')
                    except:
                        continue
                    code = pur_date.strftime("%Y%m%d")
                    total = float(rec['Tổng doanh thu'].split()[0].replace(',', ''))
                    try:
                        vat = float(rec['VAT'].split()[0].replace(',', ''))
                    except:
                        vat = 0
                    try:
                        cash = float(rec['Tiền mặt'].split()[0].replace(',', ''))
                    except:
                        cash = 0
                    try:
                        payoo = float(rec['Payoo'].split()[0].replace(',', ''))
                    except:
                        payoo = 0
                    try:
                        okara = float(rec['Okara Online'].split()[0].replace(',', ''))
                    except:
                        okara = 0
                    if cash != 0:
                        pms.append({'Name': 'CASH', 'Value': cash})
                    if payoo != 0:
                        pms.append({'Name': 'PAYOO', 'Value': payoo})
                    if okara != 0:
                        pms.append({'Name': 'OKARA', 'Value': okara})
                    count = int(rec['Số đơn hàng'])
                    for i in range(1, count):
                        ord.append({
                            'Code': f'{code}_{i}',
                            'Status': 2,
                            'PurchaseDate': f"{pur_date.strftime('%Y-%m-%d')} 14:00:00",
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
                        'PurchaseDate': f"{pur_date.strftime('%Y-%m-%d')} 14:00:00",
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
                            range=f'I{row + 2}',
                            valueInputOption='USER_ENTERED',
                            body={
                                'values': [[datetime.now().strftime('%y-%m-%d %H:%M:%S')]]
                            },
                        ).execute()
                except Exception as e:
                    submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        for _ in ord:
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=_)

