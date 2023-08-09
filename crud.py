from sqlalchemy.orm import Session

from . import models, schemas

def save_data(db: Session, data: schemas.DataCreate):
    existing_data = db.query(models.Data).filter(models.Data.Phone==data.Phone).first()
    if existing_data:
        existing_data.ReqID=data.ReqID
        db.commit()
        db.refresh(existing_data)
    else:
        db_Data=models.Data(Phone=data.Phone, ReqID=data.ReqID, Body=data.Body, num=data.num)
        db.add(db_Data)
        db.commit()
        db.refresh(db_Data)

# def get_reqid(db: Session, num: str):
#     return db.query(models.Data.ReqId).filter(models.Data.Phone==num).first()

def stat_zero(db: Session):
    return [x[0] for x in db.query(models.Data.Phone).except_(models.Data.ReqId=='50').all()]

def get_body(db: Session, phone: str):
    return db.query(models.Data.Body).filter(models.Data.Phone==phone).first()[0]

def get_num(db: Session, phone: str):
    return db.query(models.Data.num).filter(models.Data.Phone==phone).first()[0]