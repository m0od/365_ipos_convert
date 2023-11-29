import sys
from am120_timezone_amhd import AM120
from am163_nkid_amhd import AM163
from am167_mcd_amhd import AM167
from am175_tbs_amhd import AM175
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()