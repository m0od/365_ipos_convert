import time
from concurrent import futures
import multiprocessing as mp
import time
from datetime import datetime




# def init_globals(counter):
global _COUNTER
# _COUNTER = mp.Value('i', 0)
# _COUNTER = counter
def get_user_object(name):
    print(name)
    for i in range(100):
        try:
            with _COUNTER.get_lock():
                # time.sleep(1)
                _COUNTER.value += 1
                print(f't-{name} {_COUNTER.value} {datetime.now()}')
        except Exception as e:
            print(e)

def main():

    with futures.ThreadPoolExecutor(
        max_workers=2,
        # initializer=init_globals,
        # initargs=(counter,)
    ) as mt:
        mt.submit(get_user_object, '1')
        mt.submit(get_user_object, '2')
        # futures.as_completed(thread)
    # with concurrent.futures.ProcessPoolExecutor(max_workers=2,
    #     initializer=init_globals, initargs=(counter,)
    # ) as executor:
    #     executor.submit(get_user_object, range(10))
    #         # pass
    print()


if __name__ == "__main__":
    import sys
    sys.exit(main())