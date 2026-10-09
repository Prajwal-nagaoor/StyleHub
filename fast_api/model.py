from sqlalchemy import Column, String, Integer
from .database import Base
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50),nullable=False)
    password = Column(String(200), nullable=False)
    email = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
