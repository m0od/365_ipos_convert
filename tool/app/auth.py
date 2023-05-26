from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, Response

# from database import get_db
# from model import Log
# from . import database
from .database import get_db
from .model import Log, User
from google.oauth2.id_token import verify_oauth2_token as verify_oauth
from google.auth.transport import requests


def gen_token(sub, secret_key) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        'exp': expire, 'sub': sub
    }
    encoded_jwt = jwt.encode(to_encode, secret_key, 'HS256')
    return encoded_jwt


router = APIRouter()
GOOGLE_CLIENT_ID = '263581281598-tkh7tha61k78kb55c670sjfu6651m3a1.apps.googleusercontent.com'


@router.post('')
async def auth(req: Request, res: Response, db: Session = Depends(get_db), status_code=302):
    try:
        # print(req.app.extra)
        form = await req.form()
        cred = form['credential']
        info = verify_oauth(cred, requests.Request(), GOOGLE_CLIENT_ID)
        print(info)
        email = info['email']
        user = db.query(User).filter_by(email=email).first()
        if user is not None:
            # req.session['email'] = info['email']
            # print(req.session)
            user.gg_sub = info['sub']
            user.log_date = datetime.now()
            try:
                user.log_date = datetime.now()
                db.commit()
            except Exception as e:
                db.rollback()
            # generate_token(info['email'], req.app.extra['extra']['secret_key'])
            res = RedirectResponse('/dashboard')
            res.set_cookie(key='jwt', value=gen_token(email, req.app.extra['extra']['secret_key']))
            return res
        return RedirectResponse('https://adapter.pos365.vn/',
                                status_code=status.HTTP_302_FOUND)
        # info = id_token.verify_oauth2_token(req.form('credential'),
        #                                     ggRequests.Request(),
        #                                     GOOGLE_CLIENT_ID)
        #
        # print(info)
        # userId = info['sub']
        # try:
        #     session.regenerate()  # NO SESSION FIXATION FOR YOU
        # except:
        #     pass
        # session['userId'] = userId
        # return redirect('/dashboard')
    except:
        return RedirectResponse('https://adapter.pos365.vn/',
                                status_code=status.HTTP_302_FOUND)
