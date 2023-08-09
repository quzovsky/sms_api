from pydantic import BaseModel

class DataCreate(BaseModel):
    Phone: str
    ReqID: str
    Body: str
    num: str

class sendSms(BaseModel):
    SmsBody : str
    Mobiles : list[str]
    SmsNumber: str

class reqID(BaseModel):
    reqID: str
