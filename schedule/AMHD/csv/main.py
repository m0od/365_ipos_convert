import sys
from am045_ivy_amhd import AM045
from am190_koi_amhd import AM190
from am192_kohnan_amhd import AM192
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()