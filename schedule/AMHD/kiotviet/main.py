import sys
from am025_rabity_amhd import AM025
from am041_kakao_amhd import AM041
from am055_adore_amhd import AM055
from am070_wundertute_amhd import AM070
from am151_gabby_amhd import AM151
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()