# Demo policy assumptions and responsible-use boundary

GrihaSetu AI is a hackathon workflow demonstration, not an approved underwriting model, credit bureau scorecard, fraud-detection product, lender policy, legal opinion or loan decision engine.

## Illustrative default values

- Maximum FOIR: 50%.
- Maximum LTV: 80%.
- Standard bureau review threshold: 700.
- Lower demo bureau hard band: below 650.
- Bank-vs-declared income variance review trigger: above 10%; enhanced trigger above 20%.
- Interest rate: scenario-specific illustrative input.

These values exist to make deterministic demo scenarios repeatable. They are not Hero Housing Finance criteria, RBI/NHB requirements, or universal lending standards.

## Workflow controls demonstrated

- Eligibility checks use EMI, FOIR and LTV formulas.
- Mock adapters return synthetic applicant, bureau, bank, property and KYC/AML records.
- KYC, AML, income-consistency, document and property statuses are explicit scenario inputs.
- Compliance workflow gates cover credit-data consent, privacy notice, purpose limitation and fair-practices acknowledgement.
- An incomplete verification/governance control routes to REFER.
- Illustrative FOIR/LTV/bureau hard-band failures can produce a REJECT recommendation only when no higher-priority verification exception requires referral.
- Clean demo cases can produce an APPROVE recommendation.
- Every result includes reason strings, control observations, policy version and a session-level event log.

## Critical limitation

All source adapters are mocked. No third-party data is fetched, verified, authenticated or persisted. The app does not run OCR, validate signatures, inspect bank transactions, match watchlists, verify land title, or use machine learning. The event log is exportable but not tamper-proof. The controls are not a legal mapping or compliance certificate.

## Production prerequisites

Before real-world use, a lender must provide and approve credit policy, integrations and consent flows; commission legal/compliance review; implement data security, retention, access control and monitoring; validate any model; test fairness; establish human accountability and appeals; and build secure, tamper-resistant audit systems.
