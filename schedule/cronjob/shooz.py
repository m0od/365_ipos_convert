import glob
import os
import sys
from datetime import datetime
from os.path import dirname


def scan_file():
    FOLDER = 'shooz_amhd'
    FULL_PATH = f'../home/{FOLDER}/'
    EXT = '*xlsx'
    files = glob.glob(FULL_PATH + EXT)
    DATA = max(files, key=os.path.getmtime)
    t = os.path.getmtime(DATA)
    t = datetime.fromtimestamp(t).strftime('%Y%m%d %H:%M:%S')
    os.rename(DATA, f'{FULL_PATH}{t}.xlsx')


PATH = dirname(dirname(__file__))
sys.path.append(PATH)
scan_file()
