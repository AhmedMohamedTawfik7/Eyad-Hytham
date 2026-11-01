from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..errors import ApiError
from ..models import Account, DriverApplication
from ..schemas import DriverApplicationInput
from ..security import current_account
from ..serializers import application_view

router = APIRouter(prefix="/api/drivers", tags=["drivers"])


@router.post("/applications", status_code=201)
def apply(body: DriverApplicationInput, db: Session = Depends(get_db), account: Account = Depends(current_account)):
    if account.role == "operator":
        raise ApiError(422, "VALIDATION_ERROR", "Operator accounts cannot apply as drivers.")
    existing = db.scalar(select(DriverApplication).where(DriverApplication.account_id == account.id))
    if existing:
        raise ApiError(409, "CONFLICT", "A driver application already exists for this account.")
    vehicle = body.vehicle
    try:
        year = int(vehicle.get("year"))
        seats = int(vehicle["passengerSeats"]) if vehicle.get("passengerSeats") else None
        capacity = float(vehicle["freightCapacityKg"]) if vehicle.get("freightCapacityKg") else None
    except (TypeError, ValueError):
        raise ApiError(422, "VALIDATION_ERROR", "Vehicle year, seat count, or cargo capacity is invalid.")
    if year < 1980 or year > 2100 or (seats is not None and not 1 <= seats <= 50):
        raise ApiError(422, "VALIDATION_ERROR", "Vehicle details are outside the allowed range.")
    application = DriverApplication(
        account_id=account.id, home_city=body.profile.get("homeCity", ""),
        vehicle_type=vehicle.get("type", ""), vehicle_make=vehicle.get("make", ""),
        vehicle_year=year, passenger_seats=seats, freight_capacity_kg=capacity,
    )
    if len(application.home_city) < 2 or len(application.vehicle_type) < 2 or len(application.vehicle_make) < 2:
        raise ApiError(422, "VALIDATION_ERROR", "City, vehicle type, and make are required.")
    db.add(application)
    db.commit()
    db.refresh(application)
    return {"application": application_view(application)}
