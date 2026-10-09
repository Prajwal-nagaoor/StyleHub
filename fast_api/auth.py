import bcrypt
from datetime import timedelta, datetime
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .model import User
ACCESS_TOKEN_EXPIRE_MINUTES = 60
SECRET_KEY = "my-secret-key-change-this"
ALGORITHM = "HS256"
security = HTTPBearer()
def hast_password(password:str):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")
def verify_password(plain_password:str, hashed_password:str):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )
def create_access_token(user_id):
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    data = {
        "user_id":user_id,
        "exp":expire
    }

    token = jwt.encode(
        data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(security),
                     db:Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Username or password",
        headers={"WWW-Authenticate":"Bearer"}
    )
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")

        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(
            User.id == user_id
        ).first()

    if user is None:
        raise credentials_exception
    return user