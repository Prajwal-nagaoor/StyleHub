from fastapi import APIRouter, Depends, HTTPException,status, Request, Header
from .database import get_db
from .model import User,Product,Cart,Order,orderitem
from sqlalchemy.orm import Session
from .auth import get_current_user
from .schemas import orderresponse, PaymentConfirmationRequest
# stripe
import os
import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key=os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
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

        total_amount += product.product_price * i.quantity
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
@order.post("/create-payment-intent")
def create_payment_intent(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not stripe.api_key:
        raise HTTPException(
            status_code=500,
            detail="Stripe secret key is not configured",
        )

    # Find an order owned by the authenticated user.
    customer_order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
        .first()
    )

    if not customer_order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if customer_order.payment_status == "Paid":
        raise HTTPException(
            status_code=400,
            detail="This order has already been paid",
        )

    # Convert the order amount from rupees to paise.
    amount_in_paise = int(customer_order.total_payment * 100)

    if amount_in_paise <= 0:
        raise HTTPException(
            status_code=400,
            detail="Order amount must be greater than zero",
        )

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_in_paise,
            currency="inr",
            automatic_payment_methods={"enabled": True},
            metadata={
                "order_id": str(customer_order.id),
                "user_id": str(current_user.id),
            },
        )

        return {
            "order_id": customer_order.id,
            "payment_intent_id": intent.id,
            "client_secret": intent.client_secret,
            "amount": str(customer_order.total_payment),
            "currency": "inr",
            "payment_status": intent.status,
        }

    except stripe.StripeError as exc:
        raise HTTPException(
            status_code=502,
            detail="Stripe could not create the payment request",
        ) from exc


@order.post("/confirm-payment")
def confirm_payment(
    payment_data: PaymentConfirmationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Confirm a completed PaymentIntent directly after Stripe.js succeeds.
    The webhook remains enabled as a reliable asynchronous backup.
    """
    customer_order = (
        db.query(Order)
        .filter(Order.id == payment_data.order_id, Order.user_id == current_user.id)
        .first()
    )
    if not customer_order:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        intent = stripe.PaymentIntent.retrieve(payment_data.payment_intent_id)
    except stripe.StripeError as exc:
        raise HTTPException(status_code=502, detail="Unable to verify payment with Stripe") from exc

    metadata = intent.get("metadata") or {}
    if str(metadata.get("order_id")) != str(customer_order.id) or str(metadata.get("user_id")) != str(current_user.id):
        raise HTTPException(status_code=400, detail="Payment does not belong to this order")

    expected_amount = int(customer_order.total_payment * 100)
    if intent.get("amount") != expected_amount or intent.get("currency", "").lower() != "inr":
        raise HTTPException(status_code=400, detail="Payment amount or currency does not match the order")

    if intent.get("status") != "succeeded":
        return {"updated": False, "payment_status": customer_order.payment_status, "stripe_status": intent.get("status")}

    customer_order.payment_status = "Paid"
    db.commit()
    db.refresh(customer_order)
    return {"updated": True, "order_id": customer_order.id, "payment_status": customer_order.payment_status}


@order.post("/stripe-webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(
        default="",
        alias="Stripe-Signature",
    ),
    db: Session = Depends(get_db),
):
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Stripe webhook secret is not configured",
        )

    if not stripe_signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Stripe signature",
        )

    # Stripe signature verification must use the original raw request body.
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            STRIPE_WEBHOOK_SECRET,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload",
        ) from exc
    except stripe.SignatureVerificationError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature",
        ) from exc

    event_type = event["type"]

    # Ignore events unrelated to payment completion or failure.
    if event_type not in (
        "payment_intent.succeeded",
        "payment_intent.payment_failed",
    ):
        return {"received": True}

    payment_intent = event["data"]["object"]

    metadata = payment_intent.get("metadata") or {}
    order_id = metadata.get("order_id")
    user_id = metadata.get("user_id")

    # Ignore test events that aren't linked to a StyleHub order.
    if not order_id or not user_id:
        return {"received": True, "updated": False}

    try:
        order_id = int(order_id)
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid order or user ID in payment metadata",
        )

    customer_order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        .first()
    )

    if not customer_order:
        return {"received": True, "updated": False}

    # Check that the amount and currency match the order.
    expected_amount = int(customer_order.total_payment * 100)

    if payment_intent.get("amount") != expected_amount:
        raise HTTPException(
            status_code=400,
            detail="Payment amount does not match the order",
        )

    if payment_intent.get("currency", "").lower() != "inr":
        raise HTTPException(
            status_code=400,
            detail="Payment currency does not match the order currency",
        )

    try:
        if event_type == "payment_intent.succeeded":
            # Do not downgrade a successfully paid order.
            customer_order.payment_status = "Paid"

        elif event_type == "payment_intent.payment_failed":
            if customer_order.payment_status != "Paid":
                customer_order.payment_status = "Failed"

        db.commit()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not update the order payment status",
        )

    return {
        "received": True,
        "updated": True,
        "order_id": customer_order.id,
        "payment_status": customer_order.payment_status,
    }
