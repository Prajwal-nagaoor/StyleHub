from pydantic import BaseModel,EmailStr,ConfigDict

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

