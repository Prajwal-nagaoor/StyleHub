from fastapi import HTTPException, Depends, APIRouter, status
from sqlalchemy.orm import Session
from .model import User, Product
from  .database import get_db
from .auth import get_current_user, SECRET_KEY,ALGORITHM
from .schemas import ProductRequest, ProductResponse
from jose import jwt, JWTError
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)
def get_optional_user(
        credentials:HTTPAuthorizationCredentials=Depends(security),
        db:Session=Depends(get_db)):
    if not credentials:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("user_id")

        if not user_id:
            return None
        user = db.query(User).filter(
            User.id == user_id
        ).first()

        return user
    except JWTError:
        return None
pro = APIRouter(prefix="/product",tags=["prodcut"])
@pro.post("/create-product",response_model=ProductResponse)
def create_product(product_data :ProductRequest ,db:Session=Depends(get_db), current_user:Session=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized"
        )
    if not product_data.product_name or not product_data.product_desc or not product_data.product_price or not product_data.category or not product_data.stock:
        raise HTTPException(
            status_code=400,
            detail="all fields mush be filed"
        )
    if current_user.role != "seller":
        raise HTTPException(
            status_code=400,
            detail="Our not allowed to add product"
        )
    new_product = Product(
        user_id = current_user.id,
        product_name = product_data.product_name,
        product_desc = product_data.product_desc,
        product_price = product_data.product_price,
        category = product_data.category,
        stock = product_data.stock,
        
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product
@pro.get('get-product')
def view_single_prodcut(product_id:int, db:Session=Depends(get_db)):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=400,
            detail="Product not found"
        )

    return {
        "message":"Product details",
        "Product id":product_id,
        "Product name":product.product_name,
        "Product desc":product.product_desc,
        "Product price":product.product_price,
        "category":product.category,
    }

@pro.get("view_product",response_model=list[ProductResponse])
def view_product(db:Session=Depends(get_db), current_user:User=Depends(get_optional_user)):
    if current_user and current_user.role == 'seller':
        product = db.query(Product).filter(
            Product.user_id == current_user.id
        ).all()

        return product
    else:
        products= db.query(Product).all()

        return products