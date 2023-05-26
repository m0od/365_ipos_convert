from datetime import date
from pydantic import BaseModel
class Log(BaseModel):
    id = int
    rid = str
    log_date =
    type = str
    url = str
    rating = str

    class Config:
        orm_mode = True