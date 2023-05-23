import json
# from typing import Annotated

import requests
from fastapi import APIRouter, Request, Form, Response, status, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.role import auth_required

router = APIRouter()
class Item(BaseModel):
    cookie: str
    link: str

async def common_parameters(req: Request):
    print('asdkajsldjalsd')
    print(req.session)
    return {}

@router.post('/Config/VendorSession', status_code=200)
@auth_required
async def sync_session(request: Request, response: Response,cookie:str = Form(),
                       link: str = Form()):
    print('abc', request.session)
    try:
        # cookie = request.form['cookie']
        # link = request.form['link']
        b = requests.session()
        b.headers.update({
            'content-type': 'application/json',
            'cookie': f'ss-id={cookie.strip()}'
        })
        # b.cookies.update({
        #     'ss-id': cookie.strip()
        # })
        res = b.get(f'https://{link}.pos365.vn/Config/VendorSession')
        if res.status_code != 200:
            return f'Error {res.status_code}'
        tmp = res.text.split('branch :')
        # print(tmp[1][tmp[1].index(':')+1:])
        current = json.loads(tmp[1].split('}')[0] + '}')
        tmp = res.text.split('branchs:')
        branch = json.loads(tmp[1].split(']')[0] + ']')
        return {
            'current': current,
            'branch': branch
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e))
        # status_code=400
        # return str(e)