from fastapi import FastAPI, Body, HTTPException,Depends,Header
from fastapi.openapi.utils import get_openapi

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic import command
from . import crud, models, schemas
from .database import SessionLocal, engine

import httpx

import schedule
import asyncio 
import threading

import time
# def apply_migrations():
#     # Load Alembic configuration from alembic.ini
#     alembic_cfg = Config("alembic.ini")
    
#     # Connect to the database
#     db_url = alembic_cfg.attributes["sqlalchemy.url"]
#     engine = create_engine(db_url)
    
#     # Create a migration context
#     with engine.connect() as connection:
#         alembic_cfg.attributes["connection"] = connection
#         command.upgrade(alembic_cfg, "head")



app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})
models.Base.metadata.create_all(bind=engine)

# @app.on_event("startup")
# async def startup_event():
#     apply_migrations()
# swagger_url = "https://sms.parsgreen.ir/swagger/docs/v2"
# loaded_schema = httpx.get(swagger_url).json()
# app.openapi_schema = loaded_schema

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_api_key(api_key: str = Header(...)):
    return api_key

def validate_api_key(api_key: str = Depends(get_api_key)):
    if api_key != "basic apikey:2DB34FDA-16A9-4B95-9070-4F3DC796AECD":
        raise HTTPException(status_code=403, detail="Invalid API key")

async def stat_verify(db: Session = Depends(get_db)):
    nums=crud.stat_zero(db)
    if nums:
        url="https://sms.parsgreen.ir/Apiv2/Message/SmsData"
        for i in nums:
            body=crud.get_body(db,i)
            target=crud.get_num(db,i)
            res=schemas.sendSms(Mobiles=[i],SmsBody=body,SmsNumber=target)
            async with httpx.AsyncClient() as client:
                res= await client.post(url,json=res)

@app.post('/Apiv2/Message/SmsData',tags=['ApiMessage'], dependencies=[Depends(validate_api_key)])
async def recieve_and_send(Mobiles: list[str] = Body(...), SmsBody: str = Body(...), SmsNumber: str = Body(),db: Session = Depends(get_db)):
    request_schema = {
        "SmsBody": SmsBody,
        "Mobiles": Mobiles,
        "SmsNumber": SmsNumber,
    }
    url = "https://sms.parsgreen.ir/Apiv2/Message/SendSms"
    headers = {'Authorization': 'basic apikey:2DB34FDA-16A9-4B95-9070-4F3DC796AECD'}
    async with httpx.AsyncClient() as client:
        result = await client.post(url, json=request_schema,headers=headers)
        result = result.json()
    for i in range(len(Mobiles)):
        async with httpx.AsyncClient() as client:
            url2="https://sms.parsgreen.ir/Apiv2/Message/CheckDelivery"
            res2= await client.post(url2,json={"ReqID": result['DataList'][i]['ReqID']},headers=headers)
            res2=res2.json()
        res=schemas.DataCreate(Phone=result['DataList'][i]['Mobile'],ReqID=str(res2['DeliveryStatus']),Body=SmsBody,num=SmsNumber)
        crud.save_data(db,res)
    return({"Message":
            "The number has been added to the schedule."})
            
def schedule_jobs():
    schedule.every(30).minutes.do(run_stat_verify)

async def run_stat_verify():
    await stat_verify()

async def main():
    schedule_jobs()
    while True:
        schedule.run_pending()
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())



