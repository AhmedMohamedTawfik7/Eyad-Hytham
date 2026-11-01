from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RegisterInput(StrictModel):
    displayName: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=12, max_length=128)
    phone: str | None = Field(default=None, max_length=30)
    preferredLanguage: Literal["ar", "en"] = "ar"
    accountType: Literal["individual", "business"] = "individual"

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("A valid email is required.")
        return value


class LoginInput(StrictModel):
    email: str
    password: str


class AccountInput(StrictModel):
    displayName: str = Field(min_length=2, max_length=100)
    contactDetails: dict[str, str] = Field(default_factory=dict)
    preferredLanguage: Literal["ar", "en"] = "ar"
    accountType: Literal["individual", "business"] = "individual"
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=12, max_length=128)


class DriverApplicationInput(StrictModel):
    profile: dict[str, str]
    vehicle: dict


class ReviewInput(StrictModel):
    decision: Literal["approved", "rejected"]
    notes: str = Field(default="", max_length=1000)


class RequestInput(StrictModel):
    serviceType: Literal["passenger", "freight"]
    origin: str = Field(min_length=2, max_length=160)
    destination: str = Field(min_length=2, max_length=160)
    schedule: dict
    details: str = Field(min_length=1, max_length=1000)
    preferredFare: float = Field(gt=0, le=1_000_000)
    paymentMethod: Literal["cash"] = "cash"


class OfferInput(StrictModel):
    fare: float = Field(gt=0, le=1_000_000)
    message: str = Field(default="", max_length=500)
    etaMinutes: int = Field(ge=1, le=1440)


class TripUpdateInput(StrictModel):
    status: Literal["driver_en_route", "in_progress", "completed", "cancelled"] | None = None
    cashSettlementStatus: Literal["pending", "settled"] | None = None


class ReportInput(StrictModel):
    category: Literal["safety", "service", "payment", "other"]
    description: str = Field(min_length=10, max_length=2000)


class RatingInput(StrictModel):
    score: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=1000)


def contact_email(data: dict, fallback: str) -> str:
    return data.get("email", fallback)
