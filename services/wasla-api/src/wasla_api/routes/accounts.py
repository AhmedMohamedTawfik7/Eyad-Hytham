from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..errors import ApiError
from ..models import Account
from ..schemas import AccountInput
from ..security import hash_password
from ..serializers import account_view

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.post("", status_code=201)
def create_account(body: AccountInput, db: Session = Depends(get_db)):
    # Compatibility endpoint for the approved API contract; auth/register also issues a session.
    email = body.email.strip().lower()
    if db.query(Account).filter_by(email=email).first():
        raise ApiError(409, "CONFLICT", "An account with this email already exists.")
    account = Account(
        display_name=body.displayName, email=email,
        phone=body.contactDetails.get("phone"), password_hash=hash_password(body.password),
        preferred_language=body.preferredLanguage, account_type=body.accountType,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"account": account_view(account)}
