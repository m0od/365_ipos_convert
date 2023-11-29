import sys
from am067_yves_amhd import AM067
from am119_shooz_amhd import AM119
from am136_concung_amhd import AM136
from am142_routine_amhd import AM142
from am147_pnj_amhd import AM147
from am164_alfresco_amhd import AM164
from am168_mrdak_amhd import AM168
from am172_innisfree_amhd import AM172
from am189_144_amhd import AM189
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()