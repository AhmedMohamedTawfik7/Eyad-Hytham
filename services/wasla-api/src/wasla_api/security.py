import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from .db import get_db
from .errors import ApiError
from .models import Account


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        salt_hex, digest_hex = encoded.split(":", 1)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 310_000)
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def _secret() -> bytes:
    secret = os.getenv("JWT_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("JWT_SECRET must be set to at least 32 characters.")
    return secret.encode()


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def create_token(account: Account) -> str:
    now = int(time.time())
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _b64(json.dumps({
        "sub": account.id, "role": account.role, "iat": now,
        "exp": now + 60 * 60 * 8, "iss": "wasla-api", "aud": "wasla-web",
    }, separators=(",", ":")).encode())
    body = f"{header}.{payload}"
    return f"{body}.{_b64(hmac.new(_secret(), body.encode(), hashlib.sha256).digest())}"


def _decode_token(token: str) -> dict:
    try:
        header, payload, signature = token.split(".")
        body = f"{header}.{payload}"
        expected = _b64(hmac.new(_secret(), body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("signature")
        decoded_header = json.loads(base64.urlsafe_b64decode(header + "=" * (-len(header) % 4)))
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        if decoded_header.get("alg") != "HS256":
            raise ValueError("algorithm")
        if claims.get("iss") != "wasla-api" or claims.get("aud") != "wasla-web":
            raise ValueError("issuer or audience")
        if int(claims.get("exp", 0)) <= int(time.time()):
            raise ValueError("expired")
        return claims
    except Exception as exc:
        raise ApiError(401, "UNAUTHORIZED", "Your session is invalid or has expired.") from exc


def current_account(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Account:
    if not authorization or not authorization.startswith("Bearer "):
        raise ApiError(401, "UNAUTHORIZED", "Sign in to continue.")
    claims = _decode_token(authorization[7:])
    account = db.get(Account, claims.get("sub"))
    if account is None:
        raise ApiError(401, "UNAUTHORIZED", "Your account is no longer available.")
    return account


def require_role(*roles: str):
    def dependency(account: Account = Depends(current_account)) -> Account:
        if account.role not in roles:
            raise ApiError(403, "FORBIDDEN", "You do not have permission to perform this action.")
        return account
    return dependency
