from sqlalchemy import Column,Integer,String
from app.database import Base

class Student(Base):
    __tablename__  = "students"
    usn = Column(String,primary_key=True,index=True,unique=True)
    name = Column(String,index=True)
    email = Column(String,unique=True)
    age = Column(Integer)
    branch = Column(String)