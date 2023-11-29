import sys
from am169_dreamkids_amhd import AM169
from am171_mazano_amhd import AM171
from am183_tamson_amhd import AM183
from am191_249_amhd import AM191
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()