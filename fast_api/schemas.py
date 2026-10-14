from pydantic import BaseModel,EmailStr,ConfigDict
from datetime import datetime
from decimal import Decimal

class RegistrationRequest(BaseModel):
    username : str
    password : str
    email : EmailStr
    first_name : str
    last_name : str
    role : str
class RegistrationResponse(BaseModel):
    id : int
    username : str
    password : str
    email : EmailStr
    first_name : str
    last_name : str
    role : str
class LoginRequest(BaseModel):
    username :str
    password : str

class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str | None = None

class ProductRequest(BaseModel):
    product_name : str
    product_desc : str
    product_price : int
    category : str
    stock : int

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    user_id :int
    product_name : str
    product_desc : str
    product_price : int
    category : str
    stock : int
    product_image: str | None = None

class add_cart(BaseModel):
    product_id : int
    quantity : int

class add_cart_response(BaseModel):
    id : int
    user_id :int
    product_id : int
    product_name : str
    quantity:int

class orderresponse(BaseModel):
    id :int
    user_id : int
    total_payment : Decimal
    payment_status : str
    order_status : str
    createat: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentConfirmationRequest(BaseModel):
    order_id: int
    payment_intent_id: str
