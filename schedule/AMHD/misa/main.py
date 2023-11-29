import sys
from am108_sneaker_buzz import AM108
from am109_vans_amhd import AM109
if __name__ == '__main__':
    args = sys.argv[1:]
    obj = f'AM{args[0]}()'
    obj = eval(obj)
    obj.get_data()