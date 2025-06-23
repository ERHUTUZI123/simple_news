import os
import stripe
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_API_KEY")  # 推荐用 .env 变量

@router.post("/create-checkout-session")
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "TechPulse Subscription",
                    },
                    "unit_amount": 50,  # 单位是分，这里是 $0.5
                    "recurring": {"interval": "month"},
                },
                "quantity": 1,
            }],
            mode="subscription",
            automatic_tax={"enabled": True},  # 启用自动税务
            success_url="http://localhost:5173/success",
            cancel_url="http://localhost:5173/cancel",
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))