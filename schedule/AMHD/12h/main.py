import os
from os.path import dirname

if __name__ == '__main__':
    for _ in sorted(os.listdir(dirname(__file__))):
        if _.startswith('am'):
            print(_)
            try:
                eval(f"exec('from {_[:-3]} import {_.split('_')[0].upper()}')")
                obj = eval(f'{_.split("_")[0].upper()}()')
                obj.get_data()
            except Exception as e:
                print(f'{_} {e}')