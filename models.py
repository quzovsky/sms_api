from sqlalchemy import String,Column,Integer

from .database import Base


class Data(Base):

    __tablename__="Numbers"
    id= Column(Integer,primary_key=True)
    Phone= Column(String, index=True)
    ReqID= Column(String)
    Body= Column(String)
    num=Column(String)

metadata= Base.metadata