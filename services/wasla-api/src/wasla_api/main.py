import ipaddress
import logging
import os
from urllib.parse import parse_qs, urlsplit

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from . import models  # noqa: F401 - register ORM metadata
from .db import Base, SessionLocal, engine
from .errors import ApiError, api_error_handler
from .routes import accounts, auth, drivers, operations, requests, trips

app = FastAPI(title="Wasla Marketplace API", version="0.1.0")
allowed_origins = [origin.strip() for origin in os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware, allow_origins=allowed_origins, allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_exception_handler(ApiError, api_error_handler)


def validate_runtime_configuration() -> None:
    app_env = os.getenv("APP_ENV", "").strip().lower()
    if not app_env:
        raise RuntimeError("APP_ENV must be explicitly set.")
    if app_env not in {"development", "test", "staging", "production"}:
        raise RuntimeError("APP_ENV must be development, test, staging, or production.")

    secret = os.getenv("JWT_SECRET", "").strip()
    if secret and len(secret) < 32:
        raise RuntimeError("JWT_SECRET must be at least 32 characters.")

    if app_env not in {"staging", "production"}:
        return

    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url.startswith("postgresql+psycopg://"):
        raise RuntimeError(
            "Staging and production require an explicit PostgreSQL DATABASE_URL "
            "using the psycopg driver."
        )
    try:
        database_query = parse_qs(urlsplit(database_url).query)
    except ValueError:
        raise RuntimeError("DATABASE_URL must be a valid PostgreSQL connection URL.") from None
    ssl_mode = database_query.get("sslmode", [""])[0].lower()
    if ssl_mode not in {"require", "verify-ca", "verify-full"}:
        raise RuntimeError(
            "Set PostgreSQL sslmode=require or stronger for staging and production."
        )
    if len(secret) < 32 or secret.lower().startswith(
        ("replace-", "change-me", "your-secret", "example-")
    ):
        raise RuntimeError(
            "JWT_SECRET must be a non-placeholder secret with at least 32 characters."
        )
    if os.getenv("AUTO_CREATE_SCHEMA", "").strip().lower() != "false":
        raise RuntimeError("Set AUTO_CREATE_SCHEMA=false outside local development.")

    origins = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if not origins:
        raise RuntimeError("Configure CORS_ORIGINS with the deployed HTTPS web origin(s).")
    for origin in origins:
        try:
            parsed = urlsplit(origin)
            host = parsed.hostname or ""
            parsed.port
        except ValueError:
            raise RuntimeError(
                "Each staging or production CORS origin must be a public HTTPS origin "
                "without a path, query, or fragment."
            ) from None
        try:
            public_ip = ipaddress.ip_address(host).is_global
        except ValueError:
            public_ip = True
            if (
                host in {"localhost", "localhost.localdomain"}
                or host.endswith((".localhost", ".local", ".internal", ".test", ".example"))
            ):
                public_ip = False
        if (
            parsed.scheme != "https"
            or not host
            or not public_ip
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
            or "," in host
            or "*" in host
        ):
            raise RuntimeError(
                "Each staging or production CORS origin must be a public HTTPS origin "
                "without a path, query, or fragment."
            )

    if os.getenv("OPERATOR_EMAILS", "").strip():
        raise RuntimeError(
            "OPERATOR_EMAILS is development-only; provision production operators "
            "through a controlled administrative process."
        )


@app.exception_handler(IntegrityError)
async def integrity_error(_request: Request, _exc: IntegrityError):
    return JSONResponse(status_code=409, content={"error": {
        "code": "CONFLICT", "message": "This action conflicts with an existing record.",
        "details": None,
    }})


@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": {
        "code": "VALIDATION_ERROR", "message": "Please review the supplied fields.",
        # Do not echo submitted values (passwords/contact data) into error responses.
        "details": [{"location": item.get("loc"), "message": item.get("msg")} for item in exc.errors()],
    }})


@app.exception_handler(Exception)
async def unexpected_error(_request: Request, exc: Exception):
    logging.getLogger("wasla_api").exception("Unhandled API error", exc_info=exc)
    return JSONResponse(status_code=500, content={"error": {
        "code": "INTERNAL_ERROR", "message": "The service could not complete your request.",
        "details": None,
    }})


@app.on_event("startup")
def initialize_local_database():
    validate_runtime_configuration()
    if os.getenv("AUTO_CREATE_SCHEMA", "true").lower() == "true":
        Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ok", "services": {"database": "available"}}
    except Exception as exc:
        logging.getLogger("wasla_api").error(
            "Database health check failed (%s).", type(exc).__name__
        )
        return JSONResponse(status_code=503, content={
            "status": "degraded", "services": {"database": "unavailable"},
        })


for router in (auth.router, accounts.router, drivers.router, operations.router, requests.router, trips.router):
    app.include_router(router)
