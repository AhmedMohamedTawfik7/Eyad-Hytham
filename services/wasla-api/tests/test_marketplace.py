from conftest import account


def test_auth_duplicate_and_protected_access(client):
    assert client.get("/api/requests").status_code == 401
    _, headers = account(client, "Rider One", "rider@example.test")
    duplicate = client.post("/api/auth/register", json={
        "displayName": "Rider One", "email": "rider@example.test",
        "password": "correct-horse-battery", "preferredLanguage": "en",
        "accountType": "individual",
    })
    assert duplicate.status_code == 409
    assert client.get("/api/auth/me", headers=headers).status_code == 200


def test_request_offer_trip_support_and_rating_flow(client, monkeypatch):
    monkeypatch.setenv("OPERATOR_EMAILS", "ops@example.test")
    rider, rider_headers = account(client, "Rider", "rider@example.test")
    driver, driver_headers = account(client, "Driver", "driver@example.test")
    operator, operator_headers = account(client, "Operator", "ops@example.test")
    application = client.post("/api/drivers/applications", headers=driver_headers, json={
        "profile": {"homeCity": "Cairo"},
        "vehicle": {"type": "Passenger car", "make": "Sedan", "year": 2022, "passengerSeats": 3},
    })
    assert application.status_code == 201
    app_id = application.json()["application"]["id"]
    assert client.patch(f"/api/operations/driver-applications/{app_id}", headers=operator_headers,
                        json={"decision": "approved", "notes": "Profile reviewed"}).status_code == 200

    request = client.post("/api/requests", headers=rider_headers, json={
        "serviceType": "passenger", "origin": "Dokki", "destination": "Zamalek",
        "schedule": {"scheduledAt": "2026-10-29T09:30:00+03:00"},
        "details": "Two seats", "preferredFare": 180, "paymentMethod": "cash",
    })
    assert request.status_code == 201
    request_id = request.json()["request"]["id"]
    offer = client.post(f"/api/requests/{request_id}/offers", headers=driver_headers, json={
        "fare": 175, "etaMinutes": 8, "message": "Ready",
    })
    assert offer.status_code == 201
    trip_response = client.post(
        f"/api/requests/{request_id}/offers/{offer.json()['offer']['id']}/accept",
        headers=rider_headers,
    )
    assert trip_response.status_code == 201
    trip_id = trip_response.json()["trip"]["id"]
    assert client.patch(f"/api/trips/{trip_id}", headers=driver_headers,
                        json={"status": "driver_en_route"}).status_code == 200
    assert client.patch(f"/api/trips/{trip_id}", headers=driver_headers,
                        json={"status": "in_progress"}).status_code == 200
    assert client.patch(f"/api/trips/{trip_id}", headers=driver_headers,
                        json={"status": "completed"}).status_code == 200
    report = client.post(f"/api/trips/{trip_id}/reports", headers=rider_headers, json={
        "category": "service", "description": "Driver arrived later than expected.",
    })
    assert report.status_code == 201
    assert client.post(f"/api/trips/{trip_id}/ratings", headers=rider_headers,
                       json={"score": 5, "comment": "Good ride"}).status_code == 201
    assert client.post(f"/api/trips/{trip_id}/ratings", headers=rider_headers,
                       json={"score": 5}).status_code == 409


def test_unauthorized_driver_review_and_transition_rules(client):
    user, headers = account(client, "User", "user@example.test")
    response = client.get("/api/operations/driver-applications", headers=headers)
    assert response.status_code == 403
    invalid = client.post("/api/requests", headers=headers, json={
        "serviceType": "passenger", "origin": "A", "destination": "B",
        "schedule": {"scheduledAt": "soon"}, "details": "ride", "preferredFare": -1,
        "paymentMethod": "card",
    })
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"
