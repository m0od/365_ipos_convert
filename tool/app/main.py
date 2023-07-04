import os
# from functools import lru_cache

from celery import Celery
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from . import ws, api, auth, insert, extractData

# from .config import Settings

# with open('../.secret_key', 'a+b') as secret:
#     secret.seek(0)  # Seek to beginning of file since a+ mode leaves you at the end and w+ deletes the file
#     key = secret.read()
#     if not key:
#         key = os.urandom(64)
#         secret.write(key)
#         secret.flush()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=["*"],
)


# @lru_cache()
# def get_settings():
#     return Settings()
# app.add_middleware(SessionMiddleware, secret_key=key)
app.include_router(auth.router, tags=['Authenticate'])
# app.include_router(ws.router, prefix='/tool/ws', tags=['WebSocket'])
app.include_router(extractData.router, prefix='/tool/extract', tags=['Extract Data'])
app.include_router(insert.router, tags=['Import Data'])
app.include_router(api.router, prefix='/tool', tags=['Extract Data'])

# app.mount("/static", StaticFiles(directory="static"), name="static")
# html = Jinja2Templates(directory="templates")


# @app.get("/",response_class=HTMLResponse)
# async def get(req: Request):
#     return html.TemplateResponse("index.html", {"request": req})
#
# @app.get("/items/{item_id}")
# async def update_item(item_id):
#     results = {"item_id": item_id}
#     return results