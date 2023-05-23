from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
router = APIRouter()

templates = Jinja2Templates(directory="templates")

GOOGLE_CLIENT_ID = '263581281598-tkh7tha61k78kb55c670sjfu6651m3a1.apps.googleusercontent.com'

@router.get("/ping")
async def pong():
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    return {"ping": "pong!"}

@router.get("/",response_class=HTMLResponse)
def home(req: Request):
    return templates.TemplateResponse("login.html",
                                      {"request": req, 'gg_client_id':GOOGLE_CLIENT_ID})
@router.get("/dashboard",response_class=HTMLResponse)
def home(req: Request):
    try:
        req.session['userId'] = 'aaaaa'
    except:
        pass
    return templates.TemplateResponse("365.html",
                                      {"request": req})
