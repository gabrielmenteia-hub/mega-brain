from __future__ import annotations
import stripe
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db

router = APIRouter()

PLANS: dict[str, dict] = {
    "free":   {"name": "Gratuito", "sessions_per_day": 3,  "price_id": None},
    "pro":    {"name": "Pro",      "sessions_per_day": 20, "price_id": settings.STRIPE_PRICE_PRO},
    "master": {"name": "Master",   "sessions_per_day": -1, "price_id": settings.STRIPE_PRICE_MASTER},
}


@router.get("/plans")
def get_plans():
    """Public endpoint — returns available paid plans."""
    return {
        "plans": [
            {"id": "pro",    "name": "Pro",    "sessions_per_day": 20, "price_brl": 2990},
            {"id": "master", "name": "Master", "sessions_per_day": -1, "price_brl": 5990},
        ]
    }


@router.get("/status")
async def subscription_status(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
):
    user = db.table("users").select(
        "subscription_tier, subscription_expires_at"
    ).eq("id", user_id).single().execute()

    if not user.data:
        raise HTTPException(status_code=404, detail="user_not_found")

    tier = user.data.get("subscription_tier") or "free"
    plan = PLANS.get(tier, PLANS["free"])

    today = date.today().isoformat()
    sessions_res = (
        db.table("training_sessions")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .gte("created_at", today)
        .execute()
    )
    sessions_today = sessions_res.count or 0

    return {
        "plan": tier,
        "plan_name": plan["name"],
        "expires_at": user.data.get("subscription_expires_at"),
        "sessions_today": sessions_today,
        "sessions_limit": plan["sessions_per_day"],
    }


class CheckoutRequest(BaseModel):
    plan: str  # "pro" | "master"
    success_url: str = "alphachat://subscription/success"
    cancel_url: str = "alphachat://subscription/cancel"


@router.post("/checkout")
async def create_checkout(
    payload: CheckoutRequest,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="payments_not_configured")

    plan_cfg = PLANS.get(payload.plan)
    if not plan_cfg or not plan_cfg.get("price_id"):
        raise HTTPException(status_code=400, detail="invalid_plan")

    stripe.api_key = settings.STRIPE_SECRET_KEY

    user_res = db.table("users").select(
        "email, stripe_customer_id"
    ).eq("id", user_id).single().execute()
    user_data = user_res.data or {}

    customer_id = user_data.get("stripe_customer_id")
    if not customer_id:
        customer = stripe.Customer.create(
            email=user_data.get("email", ""),
            metadata={"user_id": user_id},
        )
        customer_id = customer.id
        db.table("users").update(
            {"stripe_customer_id": customer_id}
        ).eq("id", user_id).execute()

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": plan_cfg["price_id"], "quantity": 1}],
        mode="subscription",
        success_url=payload.success_url,
        cancel_url=payload.cancel_url,
        metadata={"user_id": user_id, "plan": payload.plan},
    )

    return {"checkout_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db=Depends(get_db)):
    """Stripe calls this after payment events. No JWT auth — verified by signature."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="webhook_not_configured")

    body = await request.body()
    sig = request.headers.get("stripe-signature", "")
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        event = stripe.Webhook.construct_event(body, sig, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="invalid_signature")

    etype = event["type"]

    if etype == "checkout.session.completed":
        obj = event["data"]["object"]
        uid = obj.get("metadata", {}).get("user_id")
        plan = obj.get("metadata", {}).get("plan", "pro")
        if uid:
            expires_at = (datetime.utcnow() + timedelta(days=31)).isoformat()
            db.table("users").update({
                "subscription_tier": plan,
                "subscription_expires_at": expires_at,
            }).eq("id", uid).execute()

    elif etype in ("customer.subscription.deleted", "customer.subscription.paused"):
        customer_id = event["data"]["object"]["customer"]
        user_res = (
            db.table("users")
            .select("id")
            .eq("stripe_customer_id", customer_id)
            .single()
            .execute()
        )
        if user_res.data:
            db.table("users").update({
                "subscription_tier": "free",
                "subscription_expires_at": None,
            }).eq("id", user_res.data["id"]).execute()

    elif etype == "customer.subscription.updated":
        # Handle plan changes (e.g. free → pro → master upgrades)
        obj = event["data"]["object"]
        customer_id = obj["customer"]
        status = obj.get("status")
        if status == "active":
            # Fetch plan from price metadata if available
            items = obj.get("items", {}).get("data", [])
            price_id = items[0]["price"]["id"] if items else None
            new_plan = "pro"
            for pname, pcfg in PLANS.items():
                if pcfg.get("price_id") == price_id:
                    new_plan = pname
                    break
            user_res = (
                db.table("users")
                .select("id")
                .eq("stripe_customer_id", customer_id)
                .single()
                .execute()
            )
            if user_res.data:
                expires_at = (datetime.utcnow() + timedelta(days=31)).isoformat()
                db.table("users").update({
                    "subscription_tier": new_plan,
                    "subscription_expires_at": expires_at,
                }).eq("id", user_res.data["id"]).execute()

    return {"received": True}
