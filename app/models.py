from sqlalchemy import Column, Integer, String
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    # Fix: removed redundant unique=True — primary_key already implies uniqueness
    usn = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True)
    age = Column(Integer)
    branch = Column(String)

    # Fix: added hashed_password column so the password from StudentCreate is actually stored
    hashed_password = Column(String, nullable=False)
