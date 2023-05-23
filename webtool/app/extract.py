from tasks.bg_extract import abc

from fastapi import APIRouter, Form
from fastapi.requests import Request
from fastapi.responses import Response

router = APIRouter()
@router.post('/submit')
async def x(req: Request,response: Response, txt: str=Form()):
    print(txt)
    t = abc.delay(txt)
    return {'tid': t.id}