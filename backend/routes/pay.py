import os
import stripe
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db import get_db  # Replace with your database dependency

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_API_KEY")  # Recommended to use .env variable

@router.post("/create-checkout-session")
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": "price_1RdNrDHmcVCE8q0jZJzszoap",
                "quantity": 1,
            }],
            mode="subscription",
            automatic_tax={"enabled": True},
            success_url="https://www.simplenews.online/success",
            cancel_url="https://www.simplenews.online/cancel",
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")  # Obtainable in Stripe dashboard

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        print("Webhook error:", e)
        return {"status": "invalid signature"}

    # Only handle successful payment events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
    # TODO: Implement user subscription logic
        # email = session.get("customer_email")
        # if email:
        #     user = db.query(User).filter(User.email == email).first()
        #     if user:
        #         user.is_subscribed = True
        #         db.commit()
        pass
    elif event["type"] == "customer.subscription.deleted":
    # Subscription cancellation
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
    # TODO: Implement user unsubscription logic
        # user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        # if user:
        #     user.is_subscribed = False
        #     db.commit()
        pass
    return {"status": "success"}
