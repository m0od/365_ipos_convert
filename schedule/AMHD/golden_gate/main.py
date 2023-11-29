import sys
from am150_132_amhd import AM150
from am162_139_amhd import AM162
from am179_131_amhd import AM179
from am180_73_amhd import AM180
from am182_63_amhd import AM182
from am184_70_amhd import AM184
from am188_146_amhd import AM188
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()