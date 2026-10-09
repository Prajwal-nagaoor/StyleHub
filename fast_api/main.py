from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import Base,engine, get_db
from .model import User
from .schemas import RegistrationRequest,RegistrationResponse
from .auth import hast_password, verify_password
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
    
