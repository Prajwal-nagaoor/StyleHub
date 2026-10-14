from fastapi import FastAPI, Depends, HTTPException, UploadFile,File
from sqlalchemy.orm import Session
from .database import Base,engine, get_db
from .model import User
from .schemas import RegistrationRequest,RegistrationResponse, LoginRequest, ProfileResponse
from .auth import hast_password, verify_password, create_access_token,get_current_user
from .product import pro as pro_router
from .cart import cart as cart_router
from .order import order as order_router
from fastapi.middleware.cors import CORSMiddleware
# upload image
import os
import uuid
import shutil
from pathlib import Path
from fastapi.staticfiles import StaticFiles
Base.metadata.create_all(bind=engine)
app = FastAPI()
# Serve existing product uploads to the React frontend.
UPLOAD_DIR = (Path(__file__).resolve().parent.parent / 'uploads').resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount('/uploads', StaticFiles(directory=str(UPLOAD_DIR)), name='uploads')
# upload image
# UPLOAD_DIR = Path('uploads')
# UPLOAD_DIR.mkdir(exist_ok=True)

# app.mount("uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.include_router(pro_router)
app.include_router(cart_router)
app.include_router(order_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    if registr_data.role not in ['seller','customer','admin']:
        raise HTTPException(
            status_code=400,
            detail="role must be seller or customer admin"
        )
    new_user = User(
            username = registr_data.username,
            email = registr_data.email,
            first_name = registr_data.first_name,
            last_name = registr_data.last_name,
            password = hast_password(registr_data.password),
            role = registr_data.role
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

# @app.post("/upload-product-image")
# async def upload_product_image(file: UploadFile = File(...)):
#     allowed_types = ["image/jpeg", "image/png", "image/webp"]

#     if file.content_type not in allowed_types:
#         raise HTTPException(
#             status_code=400,
#             detail="Only JPG, PNG, and WEBP images are allowed"
#         )

#     extension = Path(file.filename or "").suffix.lower()

#     if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid image extension"
#         )

#     filename = f"{uuid.uuid4().hex}{extension}"
#     file_path = UPLOAD_DIR / filename

#     try:
#         with file_path.open("wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#     finally:
#         await file.close()

#     return {
#         "message": "Image uploaded successfully",
#         "image_url": f"/uploads/{filename}"
#     }
    
    

