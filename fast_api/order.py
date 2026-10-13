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

@order.delete("/delete-order")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the order belonging to the logged-in user
    order_item = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Prevent cancellation if the order is already completed
    if order_item.order_status == "Completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completed orders cannot be cancelled"
        )

    # Get all products in this order
    items = db.query(orderitem).filter(
        orderitem.order_id == order_item.id
    ).all()

    try:
        # Restore stock for each ordered product
        for item in items:
            product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()

            if product:
                product.stock += item.quantity

        # Mark the order as cancelled
        order_item.order_status = "Cancelled"

        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to cancel order"
        )

    return {
        "message": "Order cancelled successfully",
        "order_id": order_item.id,
        "order_status": order_item.order_status
    }

@order.get("view_order",response_model=list[orderresponse])
def view_order(db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    order = db.query(Order).filter(
        Order.user_id == current_user.id
    ).all()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No orders found"
        )

    return order