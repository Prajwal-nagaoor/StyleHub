from fastapi import APIRouter, Depends, HTTPException,status
from .database import get_db
from .model import User,Product,Cart,Order,orderitem
from sqlalchemy.orm import Session
from .auth import get_current_user
from .schemas import orderresponse

order = APIRouter(prefix="/order",tags=['order'])
@order.post("/create-order", response_model=orderresponse)
def create_order(db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    cart_items = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is empty"
        )
    total_amount = 0
    for i in cart_items:
        product = db.query(Product).filter(
            Product.id == i.product_id
        ).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This Product is not found"
            )

        if i.quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Not enough stock available"
            )

        total_amount = product.product_price * i.quantity
    new_order = Order(
        user_id = current_user.id,
        total_payment = total_amount,
        payment_status = "Pending",
        order_status = "Pending"
    )
    db.add(new_order)
    db.flush()

    for i in cart_items:
        product = db.query(Product).filter(
            Product.id == i.product_id
        ).first()

        new_orderitem = orderitem(
            order_id = new_order.id,
            product_id = product.id,
            price = product.product_price,
            quantity = i.quantity,
            total_price = product.product_price * i.quantity
        )

        db.add(new_orderitem)

        product.stock -= i.quantity
    for i in cart_items:
        db.delete(i)

    db.commit()
    db.refresh(new_order)

    return new_order