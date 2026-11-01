import os
import logging

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
    if os.getenv("AUTO_CREATE_SCHEMA", "true").lower() == "true":
        Base.metadata.create_all(bind=engine)
    if os.getenv("APP_ENV", "development") != "development":
        if not os.getenv("JWT_SECRET") or len(os.getenv("JWT_SECRET", "")) < 32:
            raise RuntimeError("JWT_SECRET must be configured outside development.")


@app.get("/api/health")
def health():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ok", "services": {"database": "available"}}
    except Exception:
        return JSONResponse(status_code=503, content={
            "status": "degraded", "services": {"database": "unavailable"},
        })


for router in (auth.router, accounts.router, drivers.router, operations.router, requests.router, trips.router):
    app.include_router(router)
