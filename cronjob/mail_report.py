import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import json


def submit_error(retailer=None, reason=None):
    try:
        TELE_TOKEN = '6094052614:AAHhC8l1GKHXwBlLCHxWXySLxOSjFnvteB4'
        TELE_URL = f'https://api.telegram.org/bot{TELE_TOKEN}/sendMessage'
        HTML = f'<b>[{retailer}]</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n=> {escape(reason)}'
        DATA = {
            'chat_id': '-855515377',
            'text': HTML,
            'parse_mode': 'HTML'
        }
        requests.post(TELE_URL, data=DATA)
    except:
        pass

urls = '''am059
am061
am060
am002
am055
am100
am108
am110
am056
am043
am011
am038
am065
am063
am033
am041
am037
am102
am101
am026
am109
am016
am013
am069'''
# am125
# am126
# am124
# print(urls)
rows = ''
for domain in urls.strip().split('\n'):
    # print(domain)
    while True:
        # print(domain)
        b = requests.session()
        b.headers.update({'content-type': 'application/json'})
        r = b.post(f'https://{domain}.pos365.vn/api/auth', json={
            'Username': 'report',
            'Password': '123123123'
        })
        # print(r.text)
        if r.status_code == 200 and r.json().get('SessionId') is not None:
            try:
                vendor = b.get(f'https://{domain}.pos365.vn/Config/VendorSession').text
                retailer = json.loads(vendor.split('retailer:')[1].split('},')[0] + '}')
                p = {
                    'format': 'json',
                    'Top': '1',
                    'Filter': "PurchaseDate eq 'yesterday'"
                }
                r = b.get(f'https://{domain}.pos365.vn/api/orders', params=p)
                # print(r.text)
                if r.status_code == 200:
                    if len(r.json()['results']) == 0:
                        rows += f'''<tr>
                        <td style="border: 1px solid black;padding: 5px; text-align: left;">{domain}</td>
                        <td style="border: 1px solid black;padding: 5px; text-align: left;">{retailer['Name'].upper()}</td>
                        </tr>'''
                    break
            except Exception as e:
                print(e)
                submit_error(retailer=domain, reason=f'[REPORT] {str(e)}')
#
#
now = datetime.now() - timedelta(days=1)
port = 465  # For SSL
password = 'abqqzkkrgftlodny'
smtp_server = "smtp.gmail.com"
sender_email = "tungpt@pos365.vn"  # Enter your address
to_email = 'hadong.accounting@aeonmall-vn.com'  # Enter receiver address
cc_email = 'duongnguyen@pos365.vn'
message = MIMEMultipart("alternative")
message["Subject"] = f'Report 0 orders {now.strftime("%Y-%m-%d")}'
message["From"] = 'tungpt@pos365.vn'
message["To"] = to_email
message["Cc"] = cc_email
toAddr = [to_email, cc_email]
html = """
<html>
    <body>
        <table style="border: 1px solid black; border-collapse: collapse;">
            <thead>
                <tr>
                    <th style="border: 1px solid black; border-collapse: collapse; padding: 5px; text-align: left;">Link</th>
                    <th style="border: 1px solid black; border-collapse: collapse; padding: 5px; text-align: left;">Tenant</th>
                </tr>
            </thead>
            <tbody>{}</tbody>
        </table>
    <br />
    <div><table border="0" cellpadding="0" cellspacing="0" style="word-break:normal;color:rgba(0,0,0,0.6);font-family:&quot;YS Text&quot;,Arial,sans-serif;font-size:14px"><tbody><tr><td width="140" style="padding:0cm;width:105pt"><p align="center" style="font-family:calibri,sans-serif;font-size:11pt;margin:0cm 0cm 0.0001pt;text-align:center"><span style="font-family:arial,sans-serif"><a href="https://www.pos365.vn/?utm_source=email&amp;utm_medium=signature" rel="noopener noreferrer" title="pos365" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://www.pos365.vn/?utm_source%3Demail%26utm_medium%3Dsignature&amp;source=gmail&amp;ust=1682585070752000&amp;usg=AOvVaw3JMRE-_1NaYbtid2sIGLuj"><span style="color:rgb(153,0,153)"><img alt="logo" border="0" src="https://ci6.googleusercontent.com/proxy/iNDKzFMp9CNwbkSLzp7VOqvD05Gi8-L0UDEAMD0VPcjMy2l3H0pOGZVRMsbnEPNhygh1uK28ETVMdWUjYFH2vY5vJsycjC7SY-cyiClc1ZtXzq9cp_i7RyVZDLB35flr8MPHlfBSqPHBElQ4axk1XXfkAR76lw4djt9236rWO_Erw6wcKI-yeozlvOYfJQgT1cEuge_n23LGzPWglsUhCYBH8fyhcnhY6FdHDX__SMrLTupcauKXgshR6Rg=s0-d-e1-ft#https://resize.yandex.net/mailservice?url=https%3A%2F%2Fwww.pos365.vn%2Fstorage%2Fapp%2Fmedia%2F2020%2Flogo-365-200px.png&amp;proxy=yes&amp;key=8ff3e74b0a25bde00092352b41ea446f" width="100" style="width:1.0416in" class="CToWUd" data-bit="iit"></span></a></span></p></td><td valign="top" style="border-left:2.25pt solid rgb(238,199,45);border-top-style:none;border-right-style:none;border-bottom-style:none;border-top-width:medium;border-right-width:medium;border-bottom-width:medium;overflow:auto;padding:0cm"><table border="1" cellpadding="0" cellspacing="0" style="word-break:normal;border-bottom:2.25pt solid rgb(238,199,45);border-top-style:none;border-right-style:none;border-left-style:none;border-top-width:medium;border-right-width:medium;border-left-width:medium;margin-left:9pt"><tbody><tr><td valign="top" style="border:medium;padding:0cm 0cm 4.5pt"><p style="font-family:calibri,sans-serif;font-size:11pt;margin:0cm 0cm 0.0001pt"><strong><span style="color:rgb(238,199,45);font-family:arial,sans-serif;font-size:12pt">Phan Thanh Tùng</span></strong><br><span style="color:gray;font-family:arial,sans-serif;font-size:9pt">Developer</span></p></td></tr><tr><td valign="top" style="border:medium;padding:0cm 0cm 4.5pt"><p style="font-family:calibri,sans-serif;font-size:11pt;line-height:13.5pt;margin:0cm 0cm 0.0001pt"><span style="color:rgb(247,151,32);font-family:arial,sans-serif;font-size:9pt">m:</span><span style="color:gray;font-family:arial,sans-serif;font-size:9pt">&nbsp;038&nbsp;673&nbsp;7077&nbsp;</span><span style="color:gray;font-family:arial,sans-serif">/&nbsp;</span><span style="color:rgb(247,151,32);font-family:arial,sans-serif;font-size:9pt">h:</span><span style="color:gray;font-family:arial,sans-serif;font-size:9pt">&nbsp;1900 4515</span><br><span style="color:rgb(247,151,32);font-family:arial,sans-serif;font-size:9pt">e:</span><span style="color:gray;font-family:arial,sans-serif;font-size:9pt">&nbsp;<a href="http://hrm@pos365.vn/" rel="noopener noreferrer" target="_blank" data-saferedirecturl="https://www.google.com/url?q=http://hrm@pos365.vn/&amp;source=gmail&amp;ust=1682585070752000&amp;usg=AOvVaw2H5pCbCkrcFuawrNBGzqYJ"><span style="color:rgb(153,0,153)">tungpt@pos365.vn</span></a>/&nbsp;</span><span style="color:rgb(247,151,32);font-family:arial,sans-serif;font-size:9pt">w:</span><span style="color:gray;font-family:arial,sans-serif;font-size:9pt">&nbsp;<a href="https://www.pos365.vn/?utm_source=email&amp;utm_medium=signature" rel="noopener noreferrer" title="Trang chủ" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://www.pos365.vn/?utm_source%3Demail%26utm_medium%3Dsignature&amp;source=gmail&amp;ust=1682585070752000&amp;usg=AOvVaw3JMRE-_1NaYbtid2sIGLuj"><span style="color:rgb(153,0,153)">w<wbr>ww.pos365.vn</span></a></span></p></td></tr></tbody></table></td></tr><tr><td width="140" style="padding:4.5pt 0cm 0cm;width:105pt"><p align="center" style="font-family:calibri,sans-serif;font-size:11pt;margin:0cm 0cm 0.0001pt;text-align:center"><span style="font-family:arial,sans-serif"><a href="https://facebook.com/pos365.vn" rel="noopener noreferrer" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://facebook.com/pos365.vn&amp;source=gmail&amp;ust=1682585070752000&amp;usg=AOvVaw0IBTtEnZ8HazWGEL-WtIE-"><span style="color:rgb(153,0,153)"><img alt="facebook icon" border="0" src="https://ci5.googleusercontent.com/proxy/jh5tgWywZyiux0HmUncRZC9DDU5cAE9HrQoHb8cEs46IO4xpSwLt6netPfoKsbTWIiPfZbKYjDZdsKUZ6eRggcIrBLcW5Dt0OYkNyci67CdRWL2eVaDI_fpS0y1bgZlQhwlcQFFWQeA798rhnO6fsnIOMmTPb_BxxUt5VFx4M67U65s0y5N9jrGW7gXYu4iWr--Ojp7LE_aej8RjsH8GF7Qi5304KwLJmb7sHdwNbgQttpQL8y0GjubAPSAhbf6uKnMrQ4ljnNOudg0p4B8H3W2Eq0iY8vPRKECjGxw=s0-d-e1-ft#https://resize.yandex.net/mailservice?url=https%3A%2F%2Fcodetwocdn.azureedge.net%2Fimages%2Fmail-signatures%2Fgenerator-dm%2Fplaintext3-with-logo%2Ffb.png&amp;proxy=yes&amp;key=fc6c259975ae4295de1297951341ad76" width="16" style="width:0.1666in" class="CToWUd" data-bit="iit"></span></a>&nbsp;&nbsp;<a href="https://twitter.com/phanmempos365/" rel="noopener noreferrer" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://twitter.com/phanmempos365/&amp;source=gmail&amp;ust=1682585070752000&amp;usg=AOvVaw1Ap-adMZBe_dtylJ3j8BcV"><span style="color:rgb(153,0,153)"><img alt="twitter icon" border="0" src="https://ci5.googleusercontent.com/proxy/6dIPEkqdsNVOa6dJTUuXXRdnS5SzskRp5RktPpfIZJ7mr4vXSGQukoxQkRLTWg3C5Emur92OpKr0bPPHM4ByYYkF1WYWxFH1rGJ-lA8kF41tswLpjLIEM5BZ_XFmkV1h2PX5qjUhX9HjmbFNAxMf1dZzwtIRycQBVLQwwtNRze7Cb47OYUS3rpje5z18U4fHysspzGz_8z9vneubT6w5Q4H8idxjqk7NYrAp8kOA__iQLrhQPNq03Cp8SLos_ZDFWkt2ZJxLgAaokN9wnprK_GMo2wymOHOijZ3kypA=s0-d-e1-ft#https://resize.yandex.net/mailservice?url=https%3A%2F%2Fcodetwocdn.azureedge.net%2Fimages%2Fmail-signatures%2Fgenerator-dm%2Fplaintext3-with-logo%2Ftt.png&amp;proxy=yes&amp;key=2c7c2b0b2c9463ef07f7cb2d4c442922" width="16" style="width:0.1666in" class="CToWUd" data-bit="iit"></span></a>&nbsp;&nbsp;<a href="https://www.youtube.com/channel/UCUQoLmCDonBVlRb4U_qPTsg" rel="noopener noreferrer" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://www.youtube.com/channel/UCUQoLmCDonBVlRb4U_qPTsg&amp;source=gmail&amp;ust=1682585070752000&amp;usg=AOvVaw1zToC3qgp1HYrliTH-eo7H"><span style="color:rgb(153,0,153)"><img alt="youtube icon" border="0" src="https://ci6.googleusercontent.com/proxy/mOOMPqKUSN1wg8aebuLjQNlbPUrs8EihqLF-8eXghEE22Adz-ZgwJpWSKUPCUfK2q6FbeEM2rEc-iFVDILjoHk6jkPch7pBQ_-bMX8IUACJvbFsLVIwI0RGHuVoUiKAuFZPdtUkYJfBzJb9jhkNq9s2Ez1QWtH3yfH9cbJiytdpAT30p7ynwJa7-7piw824u5OCWUDefwPDE4Zmx2QsymH4FoOcQj-K4EKRh0xBqahecmW-1bpdmGL-P5FrPFBlUdtamolrE_6LRRd62Qhh9Acp6x516VyvQjcX3K6M=s0-d-e1-ft#https://resize.yandex.net/mailservice?url=https%3A%2F%2Fcodetwocdn.azureedge.net%2Fimages%2Fmail-signatures%2Fgenerator-dm%2Fplaintext3-with-logo%2Fyt.png&amp;proxy=yes&amp;key=5944d0e5779ae033b719f46c34cce1bb" width="16" style="width:0.1666in" class="CToWUd" data-bit="iit"></span></a>&nbsp;&nbsp;<a href="https://www.linkedin.com/company/pos365/" rel="noopener noreferrer" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://www.linkedin.com/company/pos365/&amp;source=gmail&amp;ust=1682585070753000&amp;usg=AOvVaw1LEOt1DJlDXaHXGMfM0v4b"><span style="color:rgb(153,0,153)"><img alt="linkedin icon" border="0" src="https://ci3.googleusercontent.com/proxy/a4EwcgJW8v6JJQFF25ZXZ20CBk-i1RwtabsGy5nZ23C9IWI1L0i-XG7X8WLHbcK2VgxPM0b9fNwLbtE3MuUJw3j_3OnPzUcRFPKYVmuhVEeXaTNJSCC4CORZbkrBMgWvFYGTe2TJ2EtxGL7JMDG5qUogRBFBnZQGzrf1rQNZZsWsPjJD0qxEU4FFP-nELVn1fOtKqPCZirag_KBOqBAhxYe9MFY6BSkWl-W3XQ9SHwJGr79MOwfbdDpopfYAoJ8090ZjXuZcPp5MVPAGanoShCUyY0PlBnD-ZFh4ZnQ=s0-d-e1-ft#https://resize.yandex.net/mailservice?url=https%3A%2F%2Fcodetwocdn.azureedge.net%2Fimages%2Fmail-signatures%2Fgenerator-dm%2Fplaintext3-with-logo%2Fln.png&amp;proxy=yes&amp;key=5eb17935f5984b0e078d2c89037ca528" width="16" style="width:0.1666in" class="CToWUd" data-bit="iit"></span></a>&nbsp;&nbsp;<a href="https://www.pinterest.com/pos365/" rel="noopener noreferrer" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://www.pinterest.com/pos365/&amp;source=gmail&amp;ust=1682585070753000&amp;usg=AOvVaw0m2rx9CaauWFa8nq5PJkfX"><span style="color:rgb(153,0,153)"><img alt="pinterest icon" border="0" src="https://ci6.googleusercontent.com/proxy/dY7qEW4SiEndCljrWm47728L5HEUtGFyOH_M6Yjm3fbatc1647r_B9_BeU4FhYtb_8yLUwnCeHpD7mGsL7-FgDlxmjS5OAWidPU0lRZC3m66Etc1ryJfqJachKnUcpLQImWRrs312KiGlDG0RKWaPVWebOzuwgf51SatZxgIW-CRxdCY6qA3gJdb-VSn75X-_jTSpUgUePlMmSVwOK3pjHKlNDwdWXnJxARbpyi1ty0FX-nhqJaf9WnCPRRm6Y5zwgKT2WgE1uIZQNfDMuX3mszdF2jA5ExSWAhwiPc=s0-d-e1-ft#https://resize.yandex.net/mailservice?url=https%3A%2F%2Fcodetwocdn.azureedge.net%2Fimages%2Fmail-signatures%2Fgenerator-dm%2Fplaintext3-with-logo%2Fpt.png&amp;proxy=yes&amp;key=0200d2188d2018b85074b7ee4bae13ca" width="16" style="width:0.1666in" class="CToWUd" data-bit="iit"></span></a>&nbsp;</span></p></td><td style="border-left:2.25pt solid rgb(238,199,45);border-top-style:none;border-right-style:none;border-bottom-style:none;border-top-width:medium;border-right-width:medium;border-bottom-width:medium;padding:4.5pt 0cm 0cm 9pt"><p style="font-family:calibri,sans-serif;font-size:11pt;margin:0cm 0cm 0.0001pt"><span style="font-family:arial,sans-serif"><a href="https://goo.gl/maps/TgzfHLo3DYZ3y3sk9" rel="noopener noreferrer" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://goo.gl/maps/TgzfHLo3DYZ3y3sk9&amp;source=gmail&amp;ust=1682585070753000&amp;usg=AOvVaw2K9duM30KcdPtb7hgoVqfV"><strong><span style="color:rgb(68,68,68);font-size:9pt;text-transform:uppercase">365 SOFTWARE JSC</span></strong></a><br><a href="https://goo.gl/maps/TgzfHLo3DYZ3y3sk9" rel="noopener noreferrer" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://goo.gl/maps/TgzfHLo3DYZ3y3sk9&amp;source=gmail&amp;ust=1682585070753000&amp;usg=AOvVaw2K9duM30KcdPtb7hgoVqfV"><span style="color:gray;font-size:9pt">5th floor, Tower A - Sky City Tower, 88 Lang Ha Str, Dong Da District, Ha Noi</span></a></span></p></td></tr></tbody></table></div>
    </body>
</html>
"""
if len(rows) > 0:
    part2 = MIMEText(html.strip().format(rows), 'html')
    message.attach(part2)
    ctx = ssl.create_default_context()
    while True:
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx)
            server.login(sender_email, password)
            server.sendmail(sender_email, toAddr, message.as_string())
            break
        except:
            pass