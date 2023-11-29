import sys
from am003_skechers_amhd import AM003
from am177_breadtalk_amhd import AM177
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()