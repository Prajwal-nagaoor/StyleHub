from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import Base,engine, get_db
from .model import User
from .schemas import RegistrationRequest,RegistrationResponse, LoginRequest, ProfileResponse
from .auth import hast_password, verify_password, create_access_token,get_current_user
Base.metadata.create_all(bind=engine)
app = FastAPI()
@app.get("/")
def home():
    return {
        "message":"Fastapi server is running succussfully"
    }
@app.post("/register", response_model=RegistrationResponse)
def register(registr_data:RegistrationRequest,db:Session=Depends(get_db)):
    if not registr_data.username or not registr_data.email or not registr_data.password or not registr_data.first_name:
        raise HTTPException(
            status_code=400,
            detail="All fields must required"
        )
    exists_user = db.query(User).filter(
        User.username == registr_data.username
    ).first()

    if exists_user:
        raise HTTPException(
            status_code=403,
            detail="Username already exists"
        )
        
   
    new_user = User(
            username = registr_data.username,
            email = registr_data.email,
            first_name = registr_data.first_name,
            last_name = registr_data.last_name,
            password = hast_password(registr_data.password)
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
@app.post("/login")
def login(login_data : LoginRequest,db:Session=Depends(get_db)):
    
    user = db.query(User).filter(
        User.username == login_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username or password"
        )

    if not verify_password(
        login_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Username or Password"
        )

    token = create_access_token(user.id)

    return {
        "Message": "Login Successful",
        "User id ": user.id,
        "User name":user.username,
        "access token":token,
        "token type":"Bearer"
    }

@app.get("/get-profile", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name
    }

    
    

