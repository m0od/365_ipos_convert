import sys
from am065_aokang_amhd import AM065
from am069_balabala_amhd import AM069
from am100_anta_amhd import AM100
from am101_antakids_amhd import AM101
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()