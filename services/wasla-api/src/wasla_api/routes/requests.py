from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..errors import ApiError
from ..models import Account, Offer, RideRequest, Trip
from ..schemas import OfferInput, RequestInput
from ..security import current_account, require_role
from ..serializers import offer_view, request_view, trip_view

router = APIRouter(prefix="/api/requests", tags=["requests"])


@router.post("", status_code=201)
def create_request(body: RequestInput, db: Session = Depends(get_db), account: Account = Depends(require_role("customer"))):
    request = RideRequest(
        owner_id=account.id, service_type=body.serviceType, origin=body.origin,
        destination=body.destination, scheduled_at=str(body.schedule.get("scheduledAt", "")),
        details=body.details, preferred_fare=body.preferredFare, payment_method="cash",
    )
    if len(request.scheduled_at) < 8:
        raise ApiError(422, "VALIDATION_ERROR", "A valid scheduledAt time is required.")
    db.add(request)
    db.commit()
    db.refresh(request)
    return {"request": request_view(request)}


@router.get("")
def browse_requests(
    serviceType: str | None = Query(default=None, pattern="^(passenger|freight)$"),
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db), account: Account = Depends(current_account),
):
    filters = []
    if account.active_driver:
        filters.append(RideRequest.status == "open")
    else:
        # Customers only see their own requests; other customers' exact routes stay private.
        filters.append(RideRequest.owner_id == account.id)
    if serviceType:
        filters.append(RideRequest.service_type == serviceType)

    total = db.scalar(
        select(func.count(RideRequest.id)).where(*filters)
    ) or 0
    offer_count = (
        select(func.count(Offer.id))
        .where(Offer.request_id == RideRequest.id)
        .correlate(RideRequest)
        .scalar_subquery()
    )
    query = select(RideRequest, offer_count.label("offer_count")).options(
        joinedload(RideRequest.owner)
    ).where(*filters).order_by(
        RideRequest.created_at.desc(), RideRequest.id.desc()
    ).limit(limit).offset(offset)
    rows = db.execute(query).all()
    is_driver = account.active_driver
    return {"requests": [
        request_view(
            request,
            include_private=(request.owner_id == account.id or is_driver),
            offer_count=count,
        )
        for request, count in rows
    ], "total": total}


@router.get("/{request_id}")
def get_request(request_id: str, db: Session = Depends(get_db), account: Account = Depends(current_account)):
    request = db.scalar(select(RideRequest).options(
        joinedload(RideRequest.owner), joinedload(RideRequest.offers).joinedload(Offer.driver)
    ).where(RideRequest.id == request_id))
    if request is None:
        raise ApiError(404, "NOT_FOUND", "Request was not found.")
    if request.owner_id != account.id and not account.active_driver and account.role != "operator":
        raise ApiError(403, "FORBIDDEN", "Only the requester or an approved driver can view this request.")
    trip = db.scalar(select(Trip).where(Trip.request_id == request.id))
    offers = [offer_view(row) for row in request.offers]
    return {"request": request_view(request), "offers": offers, "trip": trip_view(trip) if trip else None}


@router.post("/{request_id}/offers", status_code=201)
def create_offer(
    request_id: str, body: OfferInput, db: Session = Depends(get_db),
    driver: Account = Depends(require_role("driver")),
):
    request = db.get(RideRequest, request_id)
    if request is None:
        raise ApiError(404, "NOT_FOUND", "Request was not found.")
    if request.status != "open" or request.owner_id == driver.id:
        raise ApiError(409, "CONFLICT", "This request is not accepting offers.")
    if db.scalar(select(Offer).where(Offer.request_id == request_id, Offer.driver_id == driver.id)):
        raise ApiError(409, "CONFLICT", "You have already submitted an offer for this request.")
    offer = Offer(
        request_id=request_id, driver_id=driver.id, fare=body.fare,
        message=body.message, eta_minutes=body.etaMinutes,
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    offer.driver = driver
    return {"offer": offer_view(offer)}


@router.post("/{request_id}/offers/{offer_id}/accept", status_code=201)
def accept_offer(
    request_id: str, offer_id: str, db: Session = Depends(get_db),
    customer: Account = Depends(require_role("customer")),
):
    request = db.scalar(select(RideRequest).where(RideRequest.id == request_id).with_for_update())
    if request is None:
        raise ApiError(404, "NOT_FOUND", "Request was not found.")
    if request.owner_id != customer.id:
        raise ApiError(403, "FORBIDDEN", "Only the requester can accept an offer.")
    if request.status != "open":
        raise ApiError(409, "CONFLICT", "This request already has a selected driver.")
    offer = db.scalar(select(Offer).where(Offer.id == offer_id, Offer.request_id == request_id))
    if offer is None:
        raise ApiError(404, "NOT_FOUND", "Offer was not found for this request.")
    request.status = "matched"
    offer.status = "accepted"
    db.query(Offer).filter(Offer.request_id == request_id, Offer.id != offer_id).update({"status": "declined"})
    trip = Trip(request_id=request_id, offer_id=offer_id)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return {"trip": trip_view(trip)}
