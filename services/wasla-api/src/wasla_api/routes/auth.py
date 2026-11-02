import os

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..errors import ApiError
from ..models import Account
from ..schemas import LoginInput, RegisterInput
from ..security import create_token, current_account, hash_password, verify_password
from ..serializers import account_view

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _registration_role(email: str) -> str:
    if os.getenv("APP_ENV", "").strip().lower() not in {"development", "test"}:
        return "customer"
    operators = {
        item.strip().lower()
        for item in os.getenv("OPERATOR_EMAILS", "").split(",")
        if item.strip()
    }
    return "operator" if email in operators else "customer"


@router.post("/register", status_code=201)
def register(body: RegisterInput, db: Session = Depends(get_db)):
    if db.scalar(select(Account).where(Account.email == body.email)):
        raise ApiError(409, "CONFLICT", "An account with this email already exists.")
    account = Account(
        display_name=body.displayName, email=body.email, phone=body.phone,
        password_hash=hash_password(body.password), preferred_language=body.preferredLanguage,
        account_type=body.accountType,
        role=_registration_role(body.email),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"account": account_view(account), "accessToken": create_token(account)}


@router.post("/login")
def login(body: LoginInput, db: Session = Depends(get_db)):
    account = db.scalar(select(Account).where(Account.email == body.email.strip().lower()))
    if account is None or not verify_password(body.password, account.password_hash):
        raise ApiError(401, "UNAUTHORIZED", "Email or password is incorrect.")
    return {"account": account_view(account), "accessToken": create_token(account)}


@router.get("/me")
def me(account: Account = Depends(current_account)):
    return {"account": account_view(account)}


@router.post("/logout")
def logout(account: Account = Depends(current_account)):
    # Bearer tokens are held in memory by the client; logout discards that local token.
    return {"ok": True, "accountId": account.id}
