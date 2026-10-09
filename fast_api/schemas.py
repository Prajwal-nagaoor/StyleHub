from pydantic import BaseModel,EmailStr,ConfigDict

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
    id : int
    user_id :int
    product_name : str
    product_desc : str
    product_price : int
    category : str
    stock : int

