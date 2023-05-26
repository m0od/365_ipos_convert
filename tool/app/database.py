from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = 'mysql://root:7y!FY^netG!jn>f+@localhost/ipos365?charset=utf8mb3'
engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
)
Base = declarative_base()
Base.query = SessionLocal.query_property()

def get_db():
    global db
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
