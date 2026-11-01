from .models import Account, DriverApplication, Offer, RideRequest, Trip


def account_view(account: Account):
    return {
        "id": account.id, "displayName": account.display_name, "email": account.email,
        "phone": account.phone, "preferredLanguage": account.preferred_language,
        "accountType": account.account_type, "role": account.role,
    }


def application_view(application: DriverApplication):
    return {
        "id": application.id, "accountId": application.account_id,
        "displayName": application.account.display_name,
        "homeCity": application.home_city, "vehicleType": application.vehicle_type,
        "vehicleMake": application.vehicle_make, "vehicleYear": application.vehicle_year,
        "passengerSeats": application.passenger_seats,
        "freightCapacityKg": application.freight_capacity_kg,
        "status": application.status, "reviewNotes": application.review_notes,
        "createdAt": application.created_at.isoformat(),
    }


def offer_view(offer: Offer):
    return {
        "id": offer.id, "requestId": offer.request_id, "driverId": offer.driver_id,
        "driverName": offer.driver.display_name, "fare": offer.fare,
        "message": offer.message, "etaMinutes": offer.eta_minutes, "status": offer.status,
    }


def request_view(request: RideRequest, include_private: bool = True):
    return {
        "id": request.id, "ownerId": request.owner_id,
        "ownerName": request.owner.display_name, "serviceType": request.service_type,
        "origin": request.origin if include_private else None,
        "destination": request.destination if include_private else None,
        "schedule": {"scheduledAt": request.scheduled_at},
        "details": request.details, "preferredFare": request.preferred_fare,
        "paymentMethod": request.payment_method, "status": request.status,
        "createdAt": request.created_at.isoformat(),
        "offerCount": len(request.offers),
    }


def trip_view(trip: Trip):
    return {
        "id": trip.id, "requestId": trip.request_id, "offerId": trip.offer_id,
        "status": trip.status, "cashSettlementStatus": trip.cash_settlement_status,
    }
