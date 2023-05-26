from tasks.bg_extract import extract_product

from fastapi import APIRouter, Form
from fastapi.requests import Request
from fastapi.responses import Response

router = APIRouter()
@router.post('/products')
async def products(req: Request):
    data = await req.form()
    cookie = data['cookie']
    link = data['link']
    branch = data['branch']
    result = extract_product.delay(domain=link, cookie=cookie, branch=branch)
    # l = TechLog()
    # l.rid = str(result.id)
    # l.task_name = 'extract_product'
    # try:
    #     db.session.add(l)
    #     db.session.commit()
    # except:
    #     db.session.rollback()
    return str(result.id)
