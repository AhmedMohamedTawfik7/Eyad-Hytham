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

### One-command launch (recommended)

Install dependencies once from the repository root:

```text
python -m pip install -r services/wasla-api/requirements.txt
npm --prefix services/wasla-web ci
```

Then start both the API and web app with `python app.py` on Windows, or
`python3 app.py` on macOS/Linux if `python` is not Python 3. Open the web URL
printed by the launcher; it normally uses `https://localhost:5173` and selects
another available port if needed. The API docs URL is printed too. Press
**Ctrl+C** to stop both servers. Run `python app.py --check` to verify the
prerequisites. On first run, the launcher creates and trusts a local HTTPS
development certificate outside the repository. You can create it explicitly
with `python app.py --setup-tls`. This certificate is only for local testing;
deployed services must use a publicly trusted certificate.

The launcher is deliberately local-only: it forces SQLite, generates a fresh
development JWT secret, and uses `operator@example.test` as the local operator
account, regardless of inherited production environment variables. The secret
is regenerated after restarting, so sessions expire. Do not expose the
development servers publicly or use this launcher for production. The database
file is created as `wasla.db` in the repository root.

In PowerShell, `cd`/`Set-Location` changes directories only; do not pass it a
`python.exe` file path. If the `python` command is unavailable, invoke Python
directly, for example:

```powershell
& "C:\Path\To\python.exe" -m pip install -r services/wasla-api/requirements.txt
& "C:\Path\To\python.exe" app.py
```

Replace `C:\Path\To\python.exe` with the interpreter path reported by your
VS Code Python environment. Run these commands from the repository root.

### Manual setup (advanced)

From the repository root:

```powershell
python -m pip install -r services/wasla-api/requirements.txt
python app.py --setup-tls
$env:APP_ENV = "development"
$env:JWT_SECRET = "replace-with-a-random-local-secret-at-least-32-characters"
$env:OPERATOR_EMAILS = "operator@example.test"
$env:WASLA_TLS_CERT = "$env:LOCALAPPDATA\Wasla\certs\localhost.pem"
$env:WASLA_TLS_KEY = "$env:LOCALAPPDATA\Wasla\certs\localhost.key"
python -m uvicorn wasla_api.main:app --app-dir services/wasla-api/src --reload `
  --ssl-certfile $env:WASLA_TLS_CERT --ssl-keyfile $env:WASLA_TLS_KEY
```

In another PowerShell window, register a user with
`operator@example.test` to obtain the local operator role. All other new
accounts are regular customers. The operator email list is for local workflow
testing only and must not be used as a production identity system.

The API is at `https://localhost:8000`; interactive API documentation is at
`https://localhost:8000/docs`. The SQLite file (`wasla.db`) is created in the
current working directory. To use PostgreSQL, set `DATABASE_URL` to a
SQLAlchemy PostgreSQL URL; an optional local PostgreSQL container is described
in `docker-compose.yml`. Copy values from
[`services/wasla-api/.env.example`](services/wasla-api/.env.example) into your
own shell or secret store; the app does not load `.env` files automatically.

### 2. Start the web app

```powershell
npm --prefix services/wasla-web ci
npm --prefix services/wasla-web run dev
```

Open the localhost URL printed by Vite (normally
`https://localhost:5173`). Configure `VITE_API_URL` only if the API is hosted at
a different local address. Arabic is the default UI language; use the language
control in the header to switch to English. Session tokens are held in memory
and signing out or reloading requires signing in again.

### Installable mobile and Windows apps

The React interface can also be packaged for Android and iOS with Capacitor,
and as a Windows desktop installer with Electron. The API remains a separate
service; start it with `python app.py` before using the desktop app. These apps
connect to the API and do not provide offline trip creation or synchronization.

From `services/wasla-web`, initialize native projects once:

```powershell
npm run app:android:setup
npm run app:ios:setup
```

Build and synchronize the web interface into the native projects with
`npm run app:sync`, then open Android Studio with `npm run app:android` or Xcode
with `npm run app:ios`. Android builds require Android Studio, the Android SDK,
Java, and Gradle. iOS builds and signing require macOS and Xcode; this repository
can hold the iOS source project, but Windows cannot build or sign its app.

For an Android emulator local test, keep the API on port 8000, run
`adb reverse tcp:8000 tcp:8000`, and build with
`VITE_API_URL=https://localhost:8000`. The emulator must trust the local
development certificate; otherwise use a publicly trusted HTTPS API endpoint.
There is no cleartext fallback. Physical devices need a reachable HTTPS API
endpoint with a certificate trusted by the device. Configure it with
`VITE_API_URL` before building; never commit private keys or credentials.

For Windows, run `npm run desktop:run` for the desktop shell or
`npm run desktop:package` to create an NSIS installer under `release-final/`. Start the
local API separately before running the desktop app.
Set `WASLA_API_URL` to the API URL before launching Electron when the local API
does not use port 8000; the desktop shell forwards this value to the shared UI.

### Azure Functions local host

After installing Azure Functions Core Tools, install the Python requirements,
set `APP_ENV=development`, `JWT_SECRET`, `DATABASE_URL`, and
`OPERATOR_EMAILS`, then run `func start` from `services/wasla-api/`. The same
FastAPI application is exposed through the Functions ASGI adapter. Running
uvicorn above does not require Core Tools.

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
readiness is claimed. See [LAUNCH_READINESS.md](./LAUNCH_READINESS.md) for the
current no-go status and required sign-offs.

## Tests

```powershell
python -m pytest -c services/wasla-api/pytest.ini services/wasla-api/tests
npm --prefix services/wasla-web test
npm --prefix services/wasla-web run build
```