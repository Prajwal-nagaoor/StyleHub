
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .model import User, Product, Cart
from .database import get_db
from .schemas import add_cart, add_cart_response
from .auth import get_current_user

def add_cart(cart_data:add_cart,db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
