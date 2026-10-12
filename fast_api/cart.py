
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
