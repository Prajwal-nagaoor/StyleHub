from sqlalchemy import Column, String, Integer, ForeignKey, DECIMAL
from .database import Base
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50),nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    email = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    role = Column(String(20), nullable=True, default="customer")

class Product(Base):
    __tablename__ = "Product"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    product_desc = Column(String(500), nullable=False)
    product_price = Column(DECIMAL(10,2),nullable=False, default=0)
    category = Column(String(200), nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    user = relationship("User")


