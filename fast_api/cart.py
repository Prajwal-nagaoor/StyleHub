
from fastapi import Depends, HTTPException, status,APIRouter
from sqlalchemy.orm import Session
from .model import User, Product, Cart
from .database import get_db
from .schemas import add_cart, add_cart_response
from .auth import get_current_user

cart = APIRouter(prefix="/add-cart", tags=['add-cart'])


@cart.post("/add-cart", response_model=add_cart_response)
def add_cart(
    cart_data: add_cart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only customers can add products to the cart
    if current_user.role in ["seller", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sellers and admins cannot add products to the cart"
        )

    product = db.query(Product).filter(
        Product.id == cart_data.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Check whether the requested quantity is valid
    if cart_data.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero"
        )

    if product.stock < cart_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not enough stock available"
        )

    # Check whether this product is already in the user's cart
    cart_product = db.query(Cart).filter(
        Cart.product_id == cart_data.product_id,
        Cart.user_id == current_user.id
    ).first()

    if cart_product:
        cart_product.quantity += cart_data.quantity
    else:
        cart_product = Cart(
            user_id=current_user.id,
            product_id=product.id,
            product_name=product.product_name,
            quantity=cart_data.quantity
        )
        db.add(cart_product)

    # Reduce stock and save changes
    product.stock -= cart_data.quantity

    try:
        db.commit()
        db.refresh(cart_product)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to add product to cart"
        )

    return cart_product
@cart.get("view-cart",response_model=list[add_cart_response])
def view_cart(db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    if current_user.role in ['seller','admin']:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You are not allowed to view the cart"
        )
    cart_product = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).all()

    if not cart_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user not have any product in the cart, add the product in the cart"
        )

    return cart_product
@cart.put("/update-cart", response_model=add_cart_response)
def update_cart(cart_id:int,quantity:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    cart_product = db.query(Cart).filter(
        Cart.id == cart_id,
        Cart.user_id == current_user.id
    ).first()
    if not cart_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="quantity must be grater then 0"
        )
    product = db.query(Product).filter(
        Product.id == cart_product.product_id
    ).first()

    additional_stock = quantity - cart_product.quantity
    if product.stock < additional_stock:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not enough stock available"
        )
    

    cart_product.quantity = quantity
    product.stock -= additional_stock
    db.commit()
    db.refresh(cart_product)

    return cart_product
@cart.delete("/delte-cart")
def delete_cart(cart_id:int,db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    cart_item = db.query(Cart).filter(
        Cart.id == cart_id,
        Cart.user_id == current_user.id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="cart item not found"
        )
    product = db.query(Product).filter(
        Product.id == cart_item.product_id
    ).first()
    db.delete(cart_item)

    product.stock += cart_item.quantity
    db.commit()

    return {
        "Message":"Cart item got deleted successfully"
    }
    
