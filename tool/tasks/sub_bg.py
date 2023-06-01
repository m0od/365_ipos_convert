from os.path import dirname



if __name__:
    import sys

    PATH = dirname(dirname(dirname(__file__)))
    sys.path.append(PATH)
    from tool.pos import FullApi
    from tool.google_sheet import Sheet
    from tool.pos.product import Product
    from tool.app import api


def import_products(skip, worker):
    # try:
    data = []
    while True:
        res = api.product_list(skip, worker)
        if res['status'] == 1:
            return data
        elif res['status'] == 2:

            with _COUNTER.get_lock():
                data.extend(res['result'])
                with _COUNTER.get_lock():
                    _COUNTER.value += len(res['result'])
                    # print(_COUNTER.value)
                    r.publish(
                        channel=rid,
                        message=json.dumps({
                            'progress': f'{_COUNTER.value}/{count}',
                            'status': False})
                    )
                    # log(rid=rid, state='PROGRESS', info={'current': f'{_COUNTER.value}/{count}'})
            skip += 50 * worker