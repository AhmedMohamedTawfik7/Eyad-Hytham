# Wasla — local transport marketplace MVP

Wasla is a bilingual (Arabic/English), responsive web MVP for passenger and
freight requests in Egypt. Customers create requests and compare driver offers;
drivers apply for manual review before making offers. Accepted offers become
trips with status updates, direct cash-settlement recording, ratings, and
support reports. The initial workflow is intended for local development and
testing only; it is not legal, operational, or production launch approval.

The original examples and brand concept are preserved under [`012/`](./012/).
See [CODE_GUIDE.md](./CODE_GUIDE.md) for the repository map and limitations.

## Run locally

Requirements: Python 3.10+ (3.11/3.12 recommended), Node.js 20+, and npm.
SQLite is the default local database and the API creates its tables on startup
without inserting sample user or trip data.

### 1. Start the API

From the repository root:

```powershell
python -m pip install -r services/wasla-api/requirements.txt
$env:JWT_SECRET = "replace-with-a-random-local-secret-at-least-32-characters"
$env:OPERATOR_EMAILS = "operator@example.test"
python -m uvicorn wasla_api.main:app --app-dir services/wasla-api/src --reload
```

In another PowerShell window, register a user with
`operator@example.test` to obtain the local operator role. All other new
accounts are regular customers. The operator email list is for local workflow
testing only and must not be used as a production identity system.

The API is at `http://127.0.0.1:8000`; interactive API documentation is at
`http://127.0.0.1:8000/docs`. The SQLite file (`wasla.db`) is created in the
current working directory. To use PostgreSQL, set `DATABASE_URL` to a
SQLAlchemy PostgreSQL URL; an optional local PostgreSQL container is described
in `docker-compose.yml`. Copy values from
[`services/wasla-api/.env.example`](services/wasla-api/.env.example) into your
own shell or secret store; the app does not load `.env` files automatically.

### 2. Start the web app

```powershell
npm --prefix services/wasla-web install
npm --prefix services/wasla-web run dev
```

Open the localhost URL printed by Vite (normally
`http://localhost:5173`). Configure `VITE_API_URL` only if the API is hosted at
a different local address. Arabic is the default UI language; use the language
control in the header to switch to English. Session tokens are held in memory
and signing out or reloading requires signing in again.

### Azure Functions local host

After installing Azure Functions Core Tools, install the Python requirements,
set `JWT_SECRET`, `DATABASE_URL`, and `OPERATOR_EMAILS`, then run `func start`
from `services/wasla-api/`. The same FastAPI application is exposed through
the Functions ASGI adapter. Running uvicorn above does not require Core Tools.

## Included MVP flows

- Account registration/login, password hashing, signed expiring bearer tokens,
  and role/ownership checks.
- Passenger and freight request creation and browsing, with exact routes only
  disclosed to the owner or an approved driver.
- Driver profile applications and operator approval/rejection; only approved
  drivers can submit offers.
- Offer selection, trip progress, cash-settlement status, ratings, and support
  reports. Support reports are queued for operator review; this is not an
  emergency-response service.
- SQLite persistence for local development; PostgreSQL connection configuration
  is available, but a production migration/release process is not established.

There is no payment processing or fund custody, document upload, real identity
verification, live location tracking, fleet dispatch, or nationwide service
availability guarantee. Validate legal, privacy, safety, operational, security,
database migration, backup, monitoring, and support readiness with qualified
professionals before any public launch. No production security or legal
readiness is claimed.

## Tests

```powershell
python -m pytest -c services/wasla-api/pytest.ini services/wasla-api/tests
npm --prefix services/wasla-web test
npm --prefix services/wasla-web run build
```