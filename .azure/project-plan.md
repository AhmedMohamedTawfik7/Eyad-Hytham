# Project Plan

**Status**: Planning
**Created**: 2026-10-28
**Mode**: AUGMENT

---

## 1. Project Overview

**Goal**: Plan a bilingual, responsive web marketplace for passenger rides and freight requests in Egypt, connecting individual customers and small-business shippers with independently reviewed drivers. The initial workflow is customer request → driver fare offers → customer selection → trip status and post-trip feedback/support. The project is designed so that every module is independently testable.

**App Type**: SPA + API

**API Login**: Yes

**Mode**: AUGMENT

**Deployment Plan**: No deployment plan found

The confirmed service-area target is nationwide availability from launch. This is a material legal, safety, coverage, and operating-capacity risk: nationwide availability is a launch gate, not a claim that readiness has been established. Validate each intended service area and its support/driver coverage before enabling it; use a phased geographic rollout if nationwide readiness cannot be demonstrated.

The broad “All” answers are scoped to a practical MVP: passenger and freight request types, individual and small-business customer accounts, and driver offers that customers can compare and choose from. Fleet dispatch and fleet-management consoles, automatic assignment, direct-to-driver booking, native iOS/Android apps, document-upload workflows, digital payments, and unstaffed emergency-response promises are not assumed for this MVP. Responsive web access is planned for mobile browsers; Arabic and English localization, including RTL layout, is required.

**Commercial policy**: The owner receives 20% of the company’s net profit—not 20% of each fare. Net profit is determined after recognized platform revenue, operating costs, taxes, and approved reserves, under an agreed accounting policy. Owner distributions are periodic and documented, with reconciliations and approvals. The fare paid in cash is not itself the owner’s distribution base, and this plan does not set a platform commission or per-fare owner share. Have Egyptian counsel and an accountant validate the company, tax, accounting, and owner-agreement treatment before launch.

**Planning boundary**: The local workspace contains small or empty prototype files, not a working application, and is not connected to the specified private GitHub repository (which currently contains only `README.md`). Treat prototypes as reference material only; no application code has been scaffolded, deployed, or runtime-security-tested as part of this plan. No GitHub changes are included.

---

## 2. Backend — Azure Functions

Planning recommendation: Python Azure Functions using the Python v2 programming model and FastAPI for typed HTTP endpoints and an OpenAPI contract. The user selected Python and expressed no framework preference; FastAPI is a proposed fit, not a previously implemented or validated choice. Keep business logic, persistence, and Functions HTTP adapters independently testable. Use PostgreSQL as the system of record. Driver activation follows manual operator review; customer verification remains basic account verification unless legal discovery requires more. The MVP records cash settlement status but does not process or custody payment funds. Driver offers and customer selection are the planned matching workflow. Advanced dispatch/fleet features and document collection require separate product, operational, and legal decisions.

No uploaded documents or photos are assumed. If legal review later requires sensitive driver documents, define minimum collection, protected storage, access, retention, and deletion controls before adding uploads.

**Security and operational requirements for future implementation** (defense in depth; this plan is not evidence that these controls have been implemented or tested):

- Perform threat modeling for account takeover, privilege misuse, location exposure, trip/offer manipulation, driver impersonation, fraud, spam, and insider misuse; maintain and review mitigations as features change.
- Implement secure authentication and session handling, and authorization checks for role- and ownership-sensitive actions. Do not rely on client-side controls.
- Validate and constrain all input, encode output appropriately, and use parameterized database access for every query.
- Apply rate limits and abuse safeguards to account, request, offer, review, and support workflows; monitor suspicious activity and provide operator escalation paths.
- Keep secrets out of source control and logs; manage production secrets in Azure Key Vault. Use least-privilege access for services and operators.
- Require encryption in transit and at rest for application traffic, database data, backups, and any approved sensitive files.
- Maintain tamper-evident audit records for sensitive administrative, driver-review, support, and accounting actions; restrict and monitor access to those records.
- Include dependency and code scanning, secret scanning, and security checks in CI before release; establish remediation and release-blocking thresholds.
- Configure database backups and retention, and regularly test restoration against documented recovery objectives.
- Monitor application health, errors, security signals, and dependencies; alert on actionable incidents and maintain a documented incident-response and escalation procedure with periodic exercises.
- Minimize personal and location data; define purpose, consent/notice, retention, deletion, and access processes with local legal review. Limit location visibility and retention to the approved operational need.
- Validate transport-specific safety, fraud, complaint, and abuse scenarios; ensure support coverage is real before advertising a safety or emergency-response capability.
- Use independent security review and testing before launch and after material changes. No software or service can be represented as unhackable; risk must be reduced, monitored, and managed.

Validate Egyptian transport/platform classification, permits and licensing, driver/vehicle eligibility, passenger and freight liability and insurance, consumer disclosures, tax/invoicing, cash-settlement responsibilities, company/owner distributions, privacy and location-data obligations, retention/cross-border handling, and complaint/safety operations with qualified Egyptian counsel, accountants, insurers, and local operators. Do not treat this plan as a legal conclusion or launch authorization.

| Component | Technology |
|-----------|-----------|
| **Language** | Python |
| **Runtime** | CPython |
| **Package Manager** | pip |
| **Test Runner** | pytest |
| **Mocking Library** | unittest.mock |
| **Test Command** | pytest |
| **Orchestration** | docker-compose |

---

## 3. Frontend — Web App

Build a React + TypeScript single-page application with responsive mobile-browser layouts and Arabic/English localization, including right-to-left layout support. The MVP UI covers browsing and comparing passenger/freight requests, creating a request, viewing offers and trip status, driver application, and an operator review queue. Fleet administration and native mobile applications are deferred.

| Component | Technology |
|-----------|-----------|
| **Language** | TypeScript |
| **Framework** | React + Vite |
| **Package Manager** | npm |
| **Test Runner** | vitest |
| **Mocking Library** | vi.mock |
| **Test Command** | npm test |

---

## 4. Services Required

| Azure Service | Role in App | Environment Variable | Default Value (Local) | Classification |
|---------------|------------|---------------------|----------------------|----------------|
| Azure Functions | Python HTTP API for accounts, requests, offers, trips, driver review, ratings, and support reports | — | — | Essential |
| Azure Static Web Apps | Host the responsive Arabic/English React web client | — | — | Essential |
| Azure Database for PostgreSQL (Flexible Server) | Persist accounts, driver applications, requests, offers, trip state, ratings, support records, and auditable business records | `DATABASE_URL` | `postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/wasla_marketplace` | Essential |
| Azure Key Vault | Store production application secrets for backend use | `KEY_VAULT_URI` | Not configured locally | Essential |
| Application Insights | Application health, exception, dependency, and security-signal monitoring | `APPLICATIONINSIGHTS_CONNECTION_STRING` | Not configured locally | Enhancement |

---

## 5. Prerequisites

The local detection pass positively confirmed only the tools marked ✅. Double-check every ❓ tool and confirm supported Python/Azure Functions version compatibility before implementation. No ❌ status is used because a sandbox scan cannot prove a tool is absent.

### Run

| Tool | Service(s) | Installed | Version |
|------|------------|-----------|---------|
| Node.js | Frontend — Web App | ✅ | v26.4.0 |
| npm | Frontend — Web App | ✅ | 11.17.0 |
| CPython | Backend — Azure Functions | ✅ | Python 3.14.6 (`python`); Python 3.9.13 (`py` launcher) |
| pip | Backend — Azure Functions | ✅ | 26.1.2 (`python -m pip`) |
| Azure Functions Core Tools | Backend — Azure Functions | ❓ | — |

### Debug

| Tool | Service(s) | Installed | Version |
|------|------------|-----------|---------|
| Docker | Azure Database for PostgreSQL (local emulator) | ❓ | — |
| Docker Compose | Azure Database for PostgreSQL (local emulator) | ❓ | — |
| VS Code Azure Functions extension (`ms-azuretools.vscode-azurefunctions`) | Backend — Azure Functions | ✅ | 1.22.2 |
| VS Code Python extension (`ms-python.python`) | Backend — Azure Functions | ✅ | 2026.11.2026102101 |
| VS Code JavaScript Debugger (`ms-vscode.js-debug`) | Frontend — Web App | ❓ | — |
| VS Code Azure Static Web Apps extension (`ms-azuretools.vscode-azurestaticwebapps`) | Frontend — Web App | ✅ | 0.13.3 |

---

## 6. Design System & UI

**Component Library**: Fluent UI v9 (`@fluentui/react-components`)
**Style Direction**: A confident, clear transport marketplace with deep teal actions, warm amber trip accents, calm pale surfaces, and compact information cards that help customers compare offers. Use touch-friendly responsive layouts and RTL-aware composition for Arabic.
**Typography**: Inter, Noto Sans Arabic, system-ui

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#0B6B63` | Marketplace actions, selected trip filters, and active navigation |
| `accent`  | `#D89B32` | Fare highlights, pending driver-review markers, and trip-state accents |
| `surface` | `#F4F7F5` | Marketplace canvas and broad content areas |
| `text`    | `#17312E` | Request details, participant names, and operational labels |
| `muted`   | `#627773` | Route context, timestamps, and supporting notes |
| `border`  | `#D9E4DF` | Trip-card divisions, form boundaries, and table/grid lines |

### Pages

| Page | Route | Purpose | Layout |
|------|-------|---------|--------|
| Marketplace | `/` | Browse passenger and freight requests and compare driver offers across Egypt | `header, nav, sidebar, main, actions, card-list, tabs` |
| Create Request | `/requests/new` | Post a passenger trip or freight request with route, timing, and preferred cash fare | `header, nav, main, tabs, form, actions` |
| Request Details | `/requests/egypt-ride-2048` | Review a transport request, driver offers, and trip progress | `header, nav, main, split(two-column(meta)|list), action-bar` |
| Driver Onboarding | `/drivers/apply` | Submit a basic driver profile for manual review before activation | `header, nav, main, form, actions` |
| Operations Review | `/operations/review` | Review driver applications and trip support reports | `header, nav, sidebar, main, tabs, table, actions` |

### Sample Content

Marketplace — transport requests:
| Route / request | Service | Fare | State |
|---|---|---:|---|
| Cairo → Giza · TR-2048 | Passenger · 2 seats | EGP 180 | 3 driver offers |
| Alexandria → Cairo · FR-1182 | Freight · 6 cartons | EGP 1,250 | Open |
| Luxor → Qena · TR-2091 | Passenger · 1 seat | EGP 420 | Driver selected |

Create Request — realistic form defaults:
Passenger: Dokki, Giza → Zamalek, Cairo · 2026-10-29 09:30 · 2 seats · EGP 180 · Cash  
Freight: Sidi Gaber, Alexandria → Nasr City, Cairo · 6 cartons · EGP 1,250 · Cash

Request Details — offers for TR-2048:
| Driver | Vehicle | Offer | Arrival estimate |
|---|---|---:|---|
| Salma Hassan | Hyundai Elantra · 3 seats | EGP 175 | 8 min |
| Karim Nabil | Kia Cerato · 3 seats | EGP 190 | 5 min |
| Hossam Adel | Nissan Sunny · 3 seats | EGP 180 | 11 min |

Driver Onboarding — application examples:
| Applicant | Home city | Vehicle | Review status |
|---|---|---|---|
| Mariam Fathy | Cairo | Passenger car · 2022 | Pending |
| Youssef Samir | Alexandria | Light cargo van · 2021 | Pending |
| Nour Ehab | Luxor | Passenger car · 2020 | Pending |

Operations Review — review queue:
| Application / case | Applicant / subject | City | Status |
|---|---|---|---|
| DRV-0318 | Mariam Fathy · Passenger car | Cairo | Profile review |
| DRV-0321 | Youssef Samir · Light cargo van | Alexandria | Profile review |
| SAF-0084 | TR-1986 · Trip support report | Giza | Needs operator review |

---

## 7. Project Structure

```text
project-root/
├── .azure/
│   ├── project-plan.md
│   └── .preview-temp/
│       ├── theme.css
│       ├── manifest.json
│       ├── marketplace.html
│       ├── create-request.html
│       ├── request-details.html
│       ├── driver-onboarding.html
│       └── operations-review.html
├── .env.example
├── docker-compose.yml
├── contracts/
│   └── openapi.yaml
├── services/
│   ├── wasla-api/
│   │   ├── host.json
│   │   ├── function_app.py
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   └── wasla_api/
│   │   │       ├── handlers/
│   │   │       ├── services/
│   │   │       ├── repositories/
│   │   │       ├── models/
│   │   │       ├── schemas/
│   │   │       └── errors/
│   │   ├── migrations/
│   │   └── tests/
│   └── wasla-web/
│       ├── package.json
│       ├── vite.config.ts
│       ├── src/
│       │   ├── api/
│       │   ├── components/
│       │   ├── i18n/
│       │   └── pages/
│       └── tests/
└── 012/
    └── existing small/empty prototype files (reference only; not assumed runnable)
```

---

## 8. Route Definitions

| # | Method | Path | Description | Request Body | Response Body | Status Codes |
|---|--------|------|-------------|-------------|--------------|-------------|
| 1 | GET | `/api/health` | Health check | — | `{ status, services }` | 200, 503 |
| 2 | POST | `/api/accounts` | Create a basic marketplace account | `{ displayName, contactDetails, preferredLanguage, accountType }` | `{ account }` | 201, 409, 422 |
| 3 | POST | `/api/drivers/applications` | Submit a driver profile for manual review | `{ profile, vehicle }` | `{ application }` | 201, 409, 422 |
| 4 | GET | `/api/operations/driver-applications` | List applications for the operator review workflow | Query filters | `{ applications, total }` | 200 |
| 5 | PATCH | `/api/operations/driver-applications/{applicationId}` | Record an operator decision and review note | `{ decision, notes }` | `{ application }` | 200, 404, 422 |
| 6 | POST | `/api/requests` | Create a passenger or freight request with cash as the MVP payment method | `{ serviceType, origin, destination, schedule, details, preferredFare, paymentMethod }` | `{ request }` | 201, 422 |
| 7 | GET | `/api/requests` | Browse eligible passenger and freight requests | Query filters | `{ requests, total }` | 200 |
| 8 | GET | `/api/requests/{requestId}` | Get request details and driver offers | — | `{ request, offers, trip }` | 200, 404 |
| 9 | POST | `/api/requests/{requestId}/offers` | Submit a driver's fare offer | `{ fare, message, etaMinutes }` | `{ offer }` | 201, 404, 409, 422 |
| 10 | POST | `/api/requests/{requestId}/offers/{offerId}/accept` | Select an offer and create a trip | — | `{ trip }` | 201, 404, 409 |
| 11 | PATCH | `/api/trips/{tripId}` | Update trip progress and cash-settlement status | `{ status, cashSettlementStatus }` | `{ trip }` | 200, 404, 409, 422 |
| 12 | POST | `/api/trips/{tripId}/reports` | Submit a trip support or safety report | `{ category, description }` | `{ report }` | 201, 404, 422 |
| 13 | POST | `/api/trips/{tripId}/ratings` | Record post-trip feedback | `{ score, comment }` | `{ rating }` | 201, 404, 409, 422 |

Errors use a consistent response shape: `{ "error": { "code": "NOT_FOUND", "message": "Item not found", "details": null } }`. Validation, malformed input, missing resources, conflicts, permission failures, and unexpected errors should map to stable error codes and appropriate HTTP statuses.

---

## 9. Next Steps

1. Review and approve this plan; resolve open product, legal, compliance, and operating questions before launch commitments.
2. After separate approval for implementation, run **azure-project-scaffold** to execute the plan.
3. Run **azure-project-integrate** to wire the frontend to live data, smoke-test the backend, and create migrations.
4. Run **azure-debug-plan** → **azure-debug-generate** for Docker emulators and VS Code debugging.
5. Run the **azure-deploy** agent only when deployment is explicitly authorized and readiness, cost, quota, legal, and security gates have been reviewed.

This deliverable is limited to the project plan and frontend preview assets. No application scaffolding, GitHub changes, deployment, or runtime security claims are made here.
