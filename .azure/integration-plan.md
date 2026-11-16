# Integration hand-off — Wasla local MVP

## Status
- Frontend is already wired to the live local API; no mock client or mock dataset is used.
- Keep this as a local-testable implementation. Do not deploy or represent it as production/legal/security ready.
- No sample user, trip, offer, report, or other seed data.

## Backend
- Project: `services/wasla-api/`
- FastAPI ASGI app: `src/wasla_api/main.py`; Azure Functions v2 adapter: `function_app.py`.
- Local command (repo root): `python -m uvicorn wasla_api.main:app --app-dir services/wasla-api/src --reload`
- Default port: `8000`; health: `GET /api/health`.
- Build/check: `python -m pytest -c services/wasla-api/pytest.ini services/wasla-api/tests`

## Frontend
- Project: `services/wasla-web/`
- API seam: `src/api/client.ts`; it points to `VITE_API_URL` or `http://127.0.0.1:8000`.
- Build: `npm --prefix services/wasla-web run build`
- Dev: `npm --prefix services/wasla-web run dev`
- Tests: `npm --prefix services/wasla-web test`
- Mock files to remove: none; live API client is used by pages.
- Auth token is held in memory and sent as a bearer token; no token or private data in fixtures.

## API route inventory
- `GET /api/health`
- `POST /api/accounts`
- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`
- `POST /api/drivers/applications`
- `GET /api/operations/driver-applications`
- `PATCH /api/operations/driver-applications/{applicationId}`
- `GET /api/operations/support-reports`
- `GET /api/operations/requests`
- `POST /api/requests`, `GET /api/requests`, `GET /api/requests/{requestId}`
- `POST /api/requests/{requestId}/offers`
- `POST /api/requests/{requestId}/offers/{offerId}/accept`
- `GET /api/trips`
- `PATCH /api/trips/{tripId}`
- `POST /api/trips/{tripId}/reports`
- `POST /api/trips/{tripId}/ratings`

## Database
- Type: SQLite local default; PostgreSQL supported via `DATABASE_URL`.
- Local setup: SQLAlchemy `Base.metadata.create_all` at startup (`AUTO_CREATE_SCHEMA=true`); no seed data.
- Migration tool/directory: no versioned migration tool is configured yet; `services/wasla-api/migrations/README.md` documents the current local-only schema behavior. Create and review PostgreSQL migrations before any deployment.
- Connection variables: `DATABASE_URL`, `AUTO_CREATE_SCHEMA`; auth/operator config: `JWT_SECRET`, `OPERATOR_EMAILS`; CORS: `CORS_ORIGINS`.

## Services and scope
- Essential: FastAPI/Python API, React/Vite web client, SQLAlchemy persistence (SQLite local; PostgreSQL URL supported).
- Deferred/not implemented: live Azure deployment, payment processing/fund custody, document upload, live location tracking, fleet dispatch, verified driver identity, guaranteed national coverage, emergency-response service.
- Support reports create an operator-review record only; they do not promise an emergency response.
