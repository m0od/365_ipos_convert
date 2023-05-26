from sqlalchemy import VARCHAR
from sqlalchemy.schema import Column
from sqlalchemy.sql.functions import current_time
from sqlalchemy.types import *
from .database import Base

class Log(Base):
    __tablename__ = 'log_technical'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rid = Column(VARCHAR(36))
    log_date = Column(DateTime(), default=current_time())
    task_name = Column(Text())
    state = Column(Text())
    info = Column(JSON)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    gg_sub = Column(DECIMAL(65,0), unique=True)
    email = Column(Text, default=None)
    role = Column(Integer, default=None)
    log_date = Column(DateTime, default=current_time())