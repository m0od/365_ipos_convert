from os.path import dirname

from fastapi import APIRouter
from fastapi.requests import Request
if __name__:
    import sys

    PATH = dirname(dirname(dirname(dirname(__file__))))
    print(1, PATH)
    sys.path.append(PATH)
    from tool.tasks.products.insert import TestCeleryTask
    from tool.tasks.bg import extract_product, test
# from ...tasks.products.insert import import_product
router = APIRouter(prefix='/tool/import')


@router.post('/products')
async def products(req: Request):
    data = await req.form()
    print(data)
    cookie = data['cookie']
    link = data['link']
    branch = data['branch']
    importType = data['type']
    data = data['data']
    # result = extract_product.delay(domain=link, cookie=cookie, branch=branch)
    # result = import_product.delay(domain=link, cookie=cookie, branch=branch, importType=int(importType), data=data)
    result = test.delay()
    # l = TechLog()
    # l.rid = str(result.id)
    # l.task_name = 'extract_product'
    # try:
    #     db.session.add(l)
    #     db.session.commit()
    # except:
    #     db.session.rollback()
    return str(result.id)
