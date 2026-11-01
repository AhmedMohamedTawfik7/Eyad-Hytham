# Wasla code guide

This guide covers the Wasla local MVP and the original prototype files in
`012/`. Edit this Markdown file when source behavior changes.

## What this project is today

The repository now includes a locally testable React/TypeScript frontend and
FastAPI marketplace API. SQLite is the local default, with PostgreSQL
configuration available. It is a development MVP, not a production-ready
transport service. The files under `012/` remain examples and a static brand
demo. Several files have `.kt.py` names but are Python files, not Kotlin.

## Application source

| Path | Purpose |
|---|---|
| `services/wasla-api/src/wasla_api/main.py` | FastAPI app, health check, CORS, error mapping, and local schema initialization. |
| `services/wasla-api/src/wasla_api/routes/` | Auth, accounts, driver application/review, requests/offers, trips, support reports, and ratings endpoints. |
| `services/wasla-api/src/wasla_api/models.py` | SQLAlchemy persistence entities for accounts, requests, offers, trips, driver applications, ratings, and support reports. |
| `services/wasla-api/src/wasla_api/security.py` | PBKDF2 password hashing and signed, expiring bearer tokens. |
| `services/wasla-api/function_app.py` | Azure Functions v2 ASGI entry point for the same FastAPI app. |
| `services/wasla-api/tests/` | API tests for auth, core marketplace lifecycle, and access/validation boundaries. |
| `services/wasla-web/src/App.tsx` | Responsive React UI covering sign-in, request marketplace, request creation/details, driver application, trips, reports/ratings, and operations review. |
| `services/wasla-web/src/api/client.ts` | API client with in-memory bearer token handling. |
| `services/wasla-web/src/i18n.ts` | Arabic/English UI copy. |
| `services/wasla-web/src/styles.css` | Responsive RTL-aware design and Wasla color tokens. |
| `docker-compose.yml` | Optional local PostgreSQL container; SQLite requires no container. |

The private GitHub repository is being used to keep this source and guide
editable. Do not put real customer, driver, location, password, API-key, or
payment data in examples or commits.

## Python files

| File | What it does | Important limitations |
|---|---|---|
| `012/build.gradle.py` | Creates a minimal Flask web app. `Flask(__name__)` creates the app, `@app.route("/")` maps the home URL to `home()`, and the `if __name__ == "__main__"` block starts a local server. | Despite its filename, this is Python, not a Gradle build file. Debug mode is off, but this is still Flask's development server and is not suitable for production. The only route returns fixed text. |
| `012/app.py` | Empty placeholder. | No application code exists in this file. |
| `012/kotlin.py` | A Python dictionary with an example driver name, phone, plate, and pending status. | It is static demo data, not a driver model or verification workflow. Use invented contact and vehicle details only. |
| `012/kotlin1.py` | A Python dictionary describing a sample trip's origin, destination, weight, and price. | It has no validation, currency type, database, or trip behavior. |
| `012/kotlin2.py` | Calculates an example owner's share from company distributable net profit. | Educational arithmetic only: it is not accounting software and does not calculate legal/tax obligations. It is not a 20% deduction from an individual fare. |
| `012/kotlin3.py` | Adds two example Arabic messages to a Python list, each with a sender and message. | This is not a chat service; there is no persistence, access control, moderation, or delivery. |
| `012/kotlin4.py` | Stores an example driver ID and latitude/longitude in a Python dictionary. | Precise location is sensitive personal data. This sample is not live tracking and should never contain a real person's location. |
| `012/kotlin5.py`, `012/kotlin6.py` | Empty Python placeholders. | No code exists in these files. |
| `012/Driver.kt.py` | Empty placeholder with a Kotlin-like filename. | Despite the extension, it is not a Kotlin model. |
| `012/Message.kt.py` | Empty placeholder with a Kotlin-like filename. | Despite the extension, it is not a Kotlin model. |
| `012/Offer.kt.py` | Empty placeholder with a Kotlin-like filename. | Despite the extension, it is not a Kotlin model. |
| `012/Trip.kt.py` | Empty placeholder with a Kotlin-like filename. | Despite the extension, it is not a Kotlin model. |
| `012/gradle.py`, `012/gradle1.py` | Empty Python placeholders. | No Gradle configuration or build logic exists. |
| `012/idea.py` | Empty Python placeholder. | No code exists. |
| `012/plain text.py` | Empty file. | No code or text exists. |

### Owner profit-share example

The example in `kotlin2.py` uses four amounts:

1. **Platform revenue**: revenue earned by the company under its accounting
   policy; it is not automatically the full cash fare paid to a driver.
2. **Operating costs**: company expenses for the accounting period.
3. **Taxes**: amounts determined by the applicable accounting and tax rules.
4. **Approved reserves**: funds retained by the company under an agreed policy.

It calculates:

```text
profit after costs and taxes = platform revenue - operating costs - taxes
distributable profit = max(0, profit after costs and taxes - approved reserves)
owner distribution = 20% * distributable profit
```

For the example values in the source, platform revenue is EGP 50,000, costs are
EGP 20,000, taxes are EGP 5,000, and approved reserves are EGP 5,000. That leaves
EGP 20,000 distributable profit; the 20% owner share is EGP 4,000. Actual
distributions need a written owner agreement and review by an Egyptian
accountant and lawyer. The code is only an illustration.

## Web demo and brand files

| File | What it contains |
|---|---|
| `012/brand-demo.html` | A self-contained static concept page for a goods-delivery marketplace. Its `<style>` block defines colors, typography, cards, and responsive layouts; the HTML builds a hero, illustrative driver cards, a three-step explanation, and a profile dialog. Its small inline JavaScript only switches demo messages and opens/closes a dialog. It does not call an API or provide booking, authentication, payment, or real notifications. |
| `012/brand/campaign-copy.md` | Editable campaign headline, Arabic tagline, social caption, short voice-over, and a list of claims intentionally avoided. It explicitly describes the experience as a concept preview. |
| `012/brand/wasla-logo.svg` | Vector Wasla wordmark and connected-route icon. SVG paths, shapes, and text can be edited in a vector editor or as text. |
| `012/brand/cairo-campaign.svg` | Vector campaign illustration used in the demo. It is a visual asset, not a map or route service. |
| `012/brand/driver-nour.svg`, `012/brand/driver-karim.svg`, `012/brand/driver-salma.svg` | Fictional illustrated demo portraits. They do not represent verified or actual drivers. |

The demo has a viewport setting and a narrow-screen CSS breakpoint. Its profile
dialog uses `textContent` for displayed profile text; do not turn untrusted user
input into HTML. All labels, sample fares, ratings, and profile claims must
remain clearly marked as examples until a real service and verification process
exist.

## Existing prototype source and running

- See [README.md](./README.md) for complete local run and test instructions.
- Open `012/brand-demo.html` in a browser to view the original static concept. It uses
  local SVG assets from `012/brand/`.
- The Flask sample requires Flask to be installed. Run it locally with
  `python 012/build.gradle.py`, then visit `http://127.0.0.1:5000/`. Do not
  expose Flask's development server to the public internet.
- The legacy Python snippets can be run individually with Python. Files ending in
  `.kt.py` are still Python because `.py` is the final extension.
- Update this guide whenever a file's behavior changes. For source changes,
  commit and push them to the private GitHub remote using VS Code's Source
  Control **Sync Changes** action or the equivalent Git commands.

## Security boundary

The MVP uses development-oriented settings and is not an independently reviewed
security implementation. Authentication, input validation, and server-side
ownership checks are present but do not replace threat modeling, rate/abuse
controls, verified identity, robust audit/monitoring, encryption and managed
secret configuration, tested backups, incident response, and legal/privacy
review. SQLite `create_all` is not a production migration strategy. Do not use
this software to promise nationwide availability, emergency response, legal
compliance, or production security. No app can be guaranteed unhackable.
