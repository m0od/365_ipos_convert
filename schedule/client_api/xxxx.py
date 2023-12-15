from datetime import date, timedelta
from ftplib import FTP_TLS

import pyodbc
import os

# FTP server details
ftp_host = '103.35.65.114'
ftp_port = 21
ftp_user = 'breadtalk_amhd'
ftp_pass = 'Aeonhd@123'

yesterday = date.today() - timedelta(days=1)
SalesDate = yesterday.strftime("%Y%m%d")

# Local file to upload
# local_file_path = 'C:/Temp/S23AMHD_' + SalesDate + '.txt'
local_file_path = 'test.txt'

try:
    # Initialize an FTP_TLS instance (FTPS)
    ftps = FTP_TLS()
    ftps.set_pasv(True)

    # Connect to the FTP server
    ftps.connect(ftp_host, ftp_port)

    # Login with username and password
    ftps.login(ftp_user, ftp_pass)

    # Switch to secure data connection
    ftps.prot_p()

    # Open the local file in binary mode and upload it
    with open(local_file_path, 'rb') as local_file:
        ftps.storbinary(f'STOR {os.path.basename(local_file_path)}', local_file)

    # Close the FTP connection
    ftps.quit()

    print(f"File '{local_file_path}' uploaded successfully to '{ftp_host}'")

except Exception as e:
    print(f"Error: {str(e)}")

