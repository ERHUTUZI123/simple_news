import os
import stripe
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db import get_db  # 替换成你的数据库依赖

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_API_KEY")  # 推荐用 .env 变量

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
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")  # 在 Stripe 后台可获取

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        print("Webhook error:", e)
        return {"status": "invalid signature"}

    # 只处理支付成功的事件
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # TODO: 实现用户订阅逻辑
        # email = session.get("customer_email")
        # if email:
        #     user = db.query(User).filter(User.email == email).first()
        #     if user:
        #         user.is_subscribed = True
        #         db.commit()
        pass
    elif event["type"] == "customer.subscription.deleted":
        # 订阅取消
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        # TODO: 实现用户取消订阅逻辑
        # user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        # if user:
        #     user.is_subscribed = False
        #     db.commit()
        pass
    return {"status": "success"}
