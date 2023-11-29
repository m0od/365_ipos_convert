import sys
from am152_typo_amhd import AM152
from am153_banana_republic_amhd import AM153
from am154_tommy_amhd import AM154
from am155_cotton_on import AM155
from am156_mango_amhd import AM156
from am157_levis_amhd import AM157
from am158_nike_amhd import AM158
from am159_fitflop_amhd import AM159
from am160_gap_kids_amhd import AM160
from am161_mothercare_amhd import AM161
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()