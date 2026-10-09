from pydantic import BaseModel,EmailStr

class RegistrationRequest(BaseModel):
    username : str
    password : str
    email : EmailStr
    first_name : str
    last_name : str
class RegistrationResponse(BaseModel):
    id : int
    username : str
    password : str
    email : EmailStr
    first_name : str
    last_name : str
