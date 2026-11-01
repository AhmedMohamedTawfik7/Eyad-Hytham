from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..errors import ApiError
from ..models import Account, DriverApplication, RideRequest, SupportReport
from ..schemas import ReviewInput
from ..security import require_role
from ..serializers import application_view

router = APIRouter(prefix="/api/operations", tags=["operations"])


@router.get("/driver-applications")
def list_applications(
    status: str | None = Query(default=None, pattern="^(pending|approved|rejected)$"),
    db: Session = Depends(get_db), _operator: Account = Depends(require_role("operator")),
):
    query = select(DriverApplication).options(joinedload(DriverApplication.account))
    if status:
        query = query.where(DriverApplication.status == status)
    rows = db.scalars(query.order_by(DriverApplication.created_at.desc())).unique().all()
    return {"applications": [application_view(row) for row in rows], "total": len(rows)}


@router.patch("/driver-applications/{application_id}")
def review_application(
    application_id: str, body: ReviewInput, db: Session = Depends(get_db),
    _operator: Account = Depends(require_role("operator")),
):
    application = db.scalar(
        select(DriverApplication).options(joinedload(DriverApplication.account))
        .where(DriverApplication.id == application_id)
    )
    if application is None:
        raise ApiError(404, "NOT_FOUND", "Driver application was not found.")
    if application.status != "pending":
        raise ApiError(409, "CONFLICT", "This application has already been reviewed.")
    application.status = body.decision
    application.review_notes = body.notes
    application.reviewed_at = datetime.now(timezone.utc)
    application.account.active_driver = body.decision == "approved"
    application.account.role = "driver" if body.decision == "approved" else "customer"
    db.commit()
    db.refresh(application)
    return {"application": application_view(application)}


@router.get("/support-reports")
def list_reports(db: Session = Depends(get_db), _operator: Account = Depends(require_role("operator"))):
    rows = db.scalars(select(SupportReport).order_by(SupportReport.created_at.desc())).all()
    return {"reports": [{
        "id": row.id, "tripId": row.trip_id, "reporterId": row.reporter_id,
        "category": row.category, "description": row.description,
        "status": row.status, "createdAt": row.created_at.isoformat(),
    } for row in rows], "total": len(rows)}


@router.get("/requests")
def list_all_requests(db: Session = Depends(get_db), _operator: Account = Depends(require_role("operator"))):
    rows = db.scalars(select(RideRequest).order_by(RideRequest.created_at.desc())).all()
    return {"requests": [{
        "id": row.id, "serviceType": row.service_type, "origin": row.origin,
        "destination": row.destination, "status": row.status, "preferredFare": row.preferred_fare,
    } for row in rows], "total": len(rows)}
