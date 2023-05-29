from os.path import dirname

if __name__:
    import sys
    PATH = dirname(dirname(dirname(__file__)))
    sys.path.append(PATH)
    from tool.tasks.bg import import_product

from fastapi import APIRouter, Form
from fastapi.requests import Request
from fastapi.responses import Response

router = APIRouter()
@router.post('/products')
async def products(req: Request):
    data = await req.form()
    print(data)
    cookie = data['cookie']
    link = data['link']
    branch = data['branch']
    importType = data['type']
    data = data['data']
    result = import_product.delay(domain=link, cookie=cookie, branch=branch, importType=int(importType), data=data)
    # l = TechLog()
    # l.rid = str(result.id)
    # l.task_name = 'extract_product'
    # try:
    #     db.session.add(l)
    #     db.session.commit()
    # except:
    #     db.session.rollback()
    return str(result.id)

