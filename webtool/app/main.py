import json
from typing import Optional

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# from starlette import status

from . import auth, ws, extract

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix='/auth', tags=['Authenticate'])
app.include_router(ws.router, prefix='/ws', tags=['WebSocket'])
app.include_router(extract.router, prefix='/extract', tags=['Extract Data'])
app.mount("/static", StaticFiles(directory="static"), name="static")
html = Jinja2Templates(directory="templates")


@app.get("/",response_class=HTMLResponse)
async def get(req: Request):
    return html.TemplateResponse("index.html", {"request": req})

@app.get("/items/{item_id}")
async def update_item(item_id):
    results = {"item_id": item_id}
    return results