import sys
from am056_lemino_amhd import AM056
from am059_bloom_amhd import AM059
from am060_tgc_amhd import AM060
from am102_lock_n_lock_amhd import AM102
from am110_boo_amhd import AM110
from am113_megane_prince_amhd import AM113
from am127_elise_amhd import AM127
from am139_matviet_amhd import AM139
from am140_aristino_amhd import AM140
from am141_dchic_amhd import AM141
from am146_hoangphuc_amhd import AM146
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()