import sys
from am037_atz_amhd import AM037
from am043_jm_amhd import AM043
from am165_mulgati_amhd import AM165
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()