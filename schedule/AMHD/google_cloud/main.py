import sys
from am169_dreamkids_amhd import AM169
from am174_laneige_amhd import AM174
from am178_yanghao_amhd import AM178
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()