import os
import sys
from os.path import dirname

if __name__ == '__main__':
    try:
        args = sys.argv[1:]
    except:
        print('NO ARGUMENT')
        sys.exit(0)

    for _ in sorted(os.listdir(dirname(__file__))):
        if _.startswith(f'am{args[0]}'):
            print(_)
            try:
                eval(f"exec('from {_[:-3]} import {_.split('_')[0].upper()}')")
                obj = eval(f'{_.split("_")[0].upper()}()')
                obj.get_data()
            except Exception as e:
                print(f'20 {_} {e}')
            break

