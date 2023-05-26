import json

import requests
from fastapi import APIRouter, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import Response


from .role import auth_required

router = APIRouter()
@router.post('/sync/branch')
@auth_required
async def sync_branch(req: Request):
    try:
        data = await req.form()
        cookie = data['cookie']
        link = data['link']
        # print(data)
        b = requests.session()
        b.headers.update({
            'content-type': 'application/json',
            'cookie': f'ss-id={cookie.strip()}'
        })
        res = b.get(f'https://{link}.pos365.vn/Config/VendorSession')
        if res.status_code != 200:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Error {res.status_code}'
            )
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