from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def new_id() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    display_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    preferred_language: Mapped[str] = mapped_column(String(2), default="ar")
    account_type: Mapped[str] = mapped_column(String(20), default="individual")
    role: Mapped[str] = mapped_column(String(20), default="customer")
    active_driver: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DriverApplication(Base):
    __tablename__ = "driver_applications"
    __table_args__ = (UniqueConstraint("account_id", name="uq_driver_application_account"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    home_city: Mapped[str] = mapped_column(String(100))
    vehicle_type: Mapped[str] = mapped_column(String(80))
    vehicle_make: Mapped[str] = mapped_column(String(80))
    vehicle_year: Mapped[int] = mapped_column(Integer)
    passenger_seats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    freight_capacity_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    account: Mapped[Account] = relationship()


class RideRequest(Base):
    __tablename__ = "ride_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    service_type: Mapped[str] = mapped_column(String(20))
    origin: Mapped[str] = mapped_column(String(160))
    destination: Mapped[str] = mapped_column(String(160))
    scheduled_at: Mapped[str] = mapped_column(String(40))
    details: Mapped[str] = mapped_column(Text)
    preferred_fare: Mapped[float] = mapped_column(Float)
    payment_method: Mapped[str] = mapped_column(String(10), default="cash")
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    owner: Mapped[Account] = relationship()
    offers: Mapped[list["Offer"]] = relationship(back_populates="ride_request", cascade="all, delete-orphan")


class Offer(Base):
    __tablename__ = "offers"
    __table_args__ = (UniqueConstraint("request_id", "driver_id", name="uq_offer_driver_request"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    request_id: Mapped[str] = mapped_column(ForeignKey("ride_requests.id"), index=True)
    driver_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    fare: Mapped[float] = mapped_column(Float)
    message: Mapped[str] = mapped_column(String(500), default="")
    eta_minutes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="submitted")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    driver: Mapped[Account] = relationship()
    ride_request: Mapped[RideRequest] = relationship(back_populates="offers")


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    request_id: Mapped[str] = mapped_column(ForeignKey("ride_requests.id"), unique=True)
    offer_id: Mapped[str] = mapped_column(ForeignKey("offers.id"), unique=True)
    status: Mapped[str] = mapped_column(String(24), default="accepted")
    cash_settlement_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    offer: Mapped[Offer] = relationship()
    ride_request: Mapped[RideRequest] = relationship()


class SupportReport(Base):
    __tablename__ = "support_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id"), index=True)
    reporter_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    category: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint("trip_id", "rater_id", name="uq_rating_rater_trip"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id"), index=True)
    rater_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    ratee_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    score: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(String(1000), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
