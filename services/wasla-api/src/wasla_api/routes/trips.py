from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..errors import ApiError
from ..models import Account, Offer, Rating, RideRequest, SupportReport, Trip
from ..schemas import RatingInput, ReportInput, TripUpdateInput
from ..security import current_account
from ..serializers import trip_view

router = APIRouter(prefix="/api/trips", tags=["trips"])

TRANSITIONS = {
    "accepted": {"driver_en_route", "cancelled"},
    "driver_en_route": {"in_progress", "cancelled"},
    "in_progress": {"completed", "cancelled"},
}


def _participant_trip(db: Session, trip_id: str, account: Account):
    trip = db.scalar(select(Trip).options(
        joinedload(Trip.offer).joinedload(Offer.driver),
        joinedload(Trip.ride_request).joinedload(RideRequest.owner),
    ).where(Trip.id == trip_id))
    if trip is None:
        raise ApiError(404, "NOT_FOUND", "Trip was not found.")
    if account.id not in (trip.offer.driver_id, trip.ride_request.owner_id):
        raise ApiError(403, "FORBIDDEN", "Only trip participants can access this trip.")
    return trip


@router.patch("/{trip_id}")
def update_trip(
    trip_id: str, body: TripUpdateInput, db: Session = Depends(get_db),
    account: Account = Depends(current_account),
):
    trip = _participant_trip(db, trip_id, account)
    if body.status:
        if body.status == "cancelled" and account.id not in (trip.offer.driver_id, trip.ride_request.owner_id):
            raise ApiError(403, "FORBIDDEN", "Only trip participants can cancel this trip.")
        if body.status != "cancelled" and account.id != trip.offer.driver_id:
            raise ApiError(403, "FORBIDDEN", "Only the assigned driver can update trip progress.")
        if body.status not in TRANSITIONS.get(trip.status, set()):
            raise ApiError(409, "CONFLICT", "This trip status transition is not allowed.")
        trip.status = body.status
    if body.cashSettlementStatus:
        if trip.status != "completed":
            raise ApiError(409, "CONFLICT", "Cash settlement can only be recorded after trip completion.")
        if trip.cash_settlement_status == "settled" and body.cashSettlementStatus == "pending":
            raise ApiError(409, "CONFLICT", "Cash settlement cannot be reversed.")
        trip.cash_settlement_status = body.cashSettlementStatus
    if body.status is None and body.cashSettlementStatus is None:
        raise ApiError(422, "VALIDATION_ERROR", "Provide a trip status or cash settlement status.")
    db.commit()
    db.refresh(trip)
    return {"trip": trip_view(trip)}


@router.post("/{trip_id}/reports", status_code=201)
def create_report(
    trip_id: str, body: ReportInput, db: Session = Depends(get_db),
    account: Account = Depends(current_account),
):
    trip = _participant_trip(db, trip_id, account)
    report = SupportReport(
        trip_id=trip.id, reporter_id=account.id, category=body.category,
        description=body.description,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return {"report": {
        "id": report.id, "tripId": report.trip_id, "category": report.category,
        "description": report.description, "status": report.status,
    }}


@router.post("/{trip_id}/ratings", status_code=201)
def create_rating(
    trip_id: str, body: RatingInput, db: Session = Depends(get_db),
    account: Account = Depends(current_account),
):
    trip = _participant_trip(db, trip_id, account)
    if trip.status != "completed":
        raise ApiError(409, "CONFLICT", "Ratings are available after a trip is completed.")
    ratee_id = trip.offer.driver_id if account.id == trip.ride_request.owner_id else trip.ride_request.owner_id
    if account.id == ratee_id:
        raise ApiError(403, "FORBIDDEN", "You cannot rate yourself.")
    if db.scalar(select(Rating).where(Rating.trip_id == trip_id, Rating.rater_id == account.id)):
        raise ApiError(409, "CONFLICT", "You have already rated this trip.")
    rating = Rating(
        trip_id=trip_id, rater_id=account.id, ratee_id=ratee_id,
        score=body.score, comment=body.comment,
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return {"rating": {"id": rating.id, "score": rating.score, "comment": rating.comment}}


@router.get("")
def list_my_trips(db: Session = Depends(get_db), account: Account = Depends(current_account)):
    rows = db.scalars(select(Trip).options(
        joinedload(Trip.offer), joinedload(Trip.ride_request)
    ).join(Offer, Trip.offer_id == Offer.id).join(RideRequest, Trip.request_id == RideRequest.id)
      .where((Offer.driver_id == account.id) | (RideRequest.owner_id == account.id))
      .order_by(Trip.created_at.desc())).unique().all()
    return {"trips": [trip_view(row) for row in rows]}
