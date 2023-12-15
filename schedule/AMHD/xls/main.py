import os
import sys
from os.path import dirname

if __name__ == '__main__':
    args = sys.argv[1:]
    for _ in os.listdir(dirname(__file__)):
        if f'am{args[0]}' in _:
            eval(f"exec('from {_[:-3]} import AM{args[0]}')")
            obj = eval(f'AM{args[0]}()')
            obj.get_data()
            break