# Wasla launch readiness and approval gates

**Current decision: NO-GO for public or production launch.**

This repository is a local-testable passenger and freight marketplace MVP
targeting Egypt. Code changes and this checklist do not constitute legal advice,
regulatory clearance, an insurance confirmation, security certification, or
launch approval. Those decisions require evidence from Wasla's accountable
owner and qualified Egypt-based counsel, accountants, insurers, security
reviewers, and operating partners. Do not represent the service as approved
until the applicable sign-offs below are completed and retained.

## What is actually implemented

- The MVP supports account registration, driver applications reviewed by an
  operator, request/offer matching, trip status, cash-settlement status, ratings,
  and support reports.
- Cash is exchanged directly between trip participants; the app does not
  process or hold funds.
- Driver approval is a manual workflow, not identity, licence, vehicle, or
  insurance verification.
- Support reports are stored for operator follow-up; this is not an emergency
  response service.
- The app does not provide live location tracking, document uploads, or a
  guaranteed service area.
- Staging and production API startup now fail closed unless a PostgreSQL
  `psycopg` URL with `sslmode=require` or stronger, a non-placeholder JWT
  secret of at least 32 characters, `AUTO_CREATE_SCHEMA=false`, explicit public
  HTTPS CORS origins, and no `OPERATOR_EMAILS` allowlist are configured.
  Production operator provisioning still needs a controlled process. This is
  a technical configuration gate, not evidence that those controls are
  deployed or independently verified.

## Required gates before any public pilot

| Gate | Required evidence / accountable approval | Status |
|---|---|---|
| Company and service classification | Written Egypt-specific legal advice on company structure, marketplace/intermediary status, and whether the passenger and freight workflows require permits or other approvals. | **Open** |
| Transport permissions | Written requirements and evidence for each pilot geography, service type, drivers, vehicles, and any freight category; define how eligibility is checked and kept current. | **Open** |
| Insurance and liability | Insurer/broker confirmation of appropriate passenger, vehicle, cargo, platform, and third-party coverage; approved claims and incident procedure. | **Open** |
| Customer and driver terms | Counsel-reviewed Arabic and English terms covering the parties, platform role, fares, cash handling, cancellations, disputes, liability, complaints, and required disclosures. | **Open** |
| Privacy and data governance | Counsel-reviewed bilingual privacy notice, lawful-purpose/consent analysis, data inventory, data-subject request process, retention/deletion schedule, breach process, and review of hosting/cross-border transfers. | **Open** |
| Tax and accounting | Egypt-specific tax/invoicing treatment and documented accounting policy for revenue, costs, reserves, and any owner distributions; do not treat cash fares as company profit or owner distributions. | **Open** |
| Safety operations | Named, trained, staffed escalation owners and documented coverage hours, response targets, safety/abuse handling, law-enforcement escalation, and participant communications. Do not advertise emergency assistance without a real, tested service. | **Open** |
| Driver vetting | Defined checks, source of verification, reviewer checklist, expiry/recheck process, rejection/appeal workflow, and evidence retention approved by counsel and insurer. Current manual approval alone is insufficient. | **Open** |
| Geographic scope | Named pilot areas with demonstrated driver supply, support capacity, insurance, and legal clearance. Disable unapproved areas; do not claim nationwide coverage without evidence. | **Open** |
| User lifecycle | Approved account verification, password recovery, account closure/deletion, access/correction requests, and retention handling. These workflows are not currently implemented. | **Open** |
| Security and privacy review | Threat model, independent review, remediation of launch-blocking findings, dependency/secret scanning, rate/abuse controls, least-privilege operator access, and secure production configuration review. | **Open** |
| Database and recovery | Reviewed, versioned PostgreSQL migrations; backup policy and retention; a successful restore exercise against approved recovery objectives. Production migrations/backups are not established. | **Open** |
| Reliability and support | Production monitoring and actionable alerts, on-call ownership, incident response and rollback runbooks, service objectives, capacity test, and support staffing evidence. | **Open** |
| Release validation | Clean reproducible dependency installs, backend and frontend tests/build, deployment smoke tests, accessibility/RTL checks, and a reviewed release/rollback record. Frontend dependency installation/build remains unverified in this checkout. | **Open** |

## Approval record

No signatures or approvals are recorded here. Complete this record only after
the evidence is reviewed; attach or reference the evidence in an access-
controlled location, not in this public repository.

| Approval | Name / organization | Evidence reference | Date | Decision |
|---|---|---|---|---|
| Accountable business owner |  |  |  | Pending |
| Egypt-qualified legal counsel |  |  |  | Pending |
| Tax/accounting professional |  |  |  | Pending |
| Insurance provider/broker |  |  |  | Pending |
| Safety and customer-operations lead |  |  |  | Pending |
| Security reviewer |  |  |  | Pending |
| Production engineering/release owner |  |  |  | Pending |

The launch decision remains **NO-GO** while any required gate is open. A public
pilot, if later approved, should be limited to the exact geography, service
types, operating hours, and capacity supported by the evidence and staffing.
