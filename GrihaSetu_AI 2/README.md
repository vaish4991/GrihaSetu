# GrihaSetu AI — End-to-End Explainable Mortgage Underwriting Demo

**Track:** Hero Housing Fintech Challenge  
**Problem statement:** Digitally Automated Mortgage Underwriting Engine  
**Format:** Streamlit application + deterministic underwriting rules + synthetic connector adapters + audit export

GrihaSetu AI demonstrates an end-to-end mortgage underwriting workflow for a hackathon: application intake, multi-source data aggregation, affordability/policy checks, KYC/AML and fraud-indicator routing, risk signals, document/property readiness, compliance workflow gates, approve/reject/refer demo recommendations, and an explainable audit trail.

> **Important boundary:** All external source responses are synthetic simulations. No bank, credit bureau, account aggregator, KYC/AML provider or property registry is contacted. The app does not authenticate documents, use a trained ML model, certify regulatory compliance, or make a real credit decision. Approve/reject/refer outputs are illustrative demo recommendations only. Do not enter real customer data.

## Eight-point challenge coverage

| Challenge requirement | What this prototype demonstrates | Limitation stated honestly |
|---|---|---|
| 1. Integrate data sources | Five labelled adapters: applicant intake, mock bureau, mock bank, mock property and mock KYC/AML | Synthetic fixtures only; no live external API integration |
| 2. Eligibility and policy | EMI, FOIR, LTV, fit-cap maths and configurable policy thresholds | Demo policy values, not lender policy |
| 3. Fraud detection and KYC/AML | Mock screening statuses, identity/bank/employer exception flags and variance triggers | Rules and synthetic outcomes; not vendor verification or an ML fraud model |
| 4. Risk scoring | Transparent deterministic review points and visible reason codes | Not a trained scorecard or probability of default |
| 5. Documents and property | Document availability checklist and simulated title-status review | No upload/OCR/signature authentication/legal title search |
| 6. Compliance checks | Consent, privacy notice, purpose-limitation and fair-practices workflow gates | Demonstration controls only; not legal advice or regulatory certification |
| 7. Instant decisioning | APPROVE / REJECT / REFER recommendations under demo rules | Not a loan sanction, offer or final lender decision |
| 8. Explainability and governance | Control trace, policy version, case event log and CSV/JSON downloads | Session-level demo audit; not tamper-proof production logging |

## Architecture

```text
Streamlit borrower / reviewer workspace
  ├── Applicant & loan intake
  ├── Synthetic multi-source adapters (core/integrations.py)
  │     ├── Applicant intake
  │     ├── Mock credit bureau
  │     ├── Mock bank / account aggregator
  │     ├── Mock property registry
  │     └── Mock KYC / AML screening
  ├── Eligibility calculations (core/engine.py)
  │     ├── EMI / FOIR / LTV / illustrative fit cap
  │     └── Configurable demo policy + explainable review points
  ├── End-to-end orchestrator (core/underwriting.py)
  │     ├── KYC / AML / fraud-indicator checks
  │     ├── Document / property status checks
  │     ├── Compliance workflow gates
  │     └── APPROVE / REJECT / REFER demo recommendation
  └── Explainability and governance
        ├── Control-by-control trace
        ├── Policy version
        ├── Case event log
        └── CSV summary + JSON audit export
```

## Run locally

Python 3.10+ is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Demo scenarios

Use the sidebar to load one of three synthetic cases:

1. **Balanced — approve recommendation:** all demo gates pass and the configured policy thresholds are met.
2. **Evidence exception — refer recommendation:** synthetic KYC review, document gap, income variance and property review trigger referral.
3. **Affordability breach — reject recommendation:** illustrative FOIR/LTV/score hard bands are breached while verification gates are otherwise clear.

Then click **Run end-to-end underwriting**. Explore the decision explanation, data lineage, controls and audit tabs. Download the case summary CSV and audit JSON.

## Tests

```bash
python -m pytest -q
```

The tests cover EMI and affordability calculations, all three decision outcomes, consent gating, synthetic connector provenance and audit events.

## Deploy (optional)

Deploy `app.py` to a Python/Streamlit-compatible host and install from `requirements.txt`. Keep secrets out of the repository. This demo currently requires no API secrets because all connectors are synthetic. Do not upload real customer documents or personal information.

## Responsible deployment requirements

A production implementation would require (at minimum) lender-approved policy, authenticated and consented integrations, secure handling of personal data, verified document and property checks, approved KYC/AML providers, legal/compliance review, access controls, encryption, retention rules, bias/fairness and model validation, adverse-action processes, operational monitoring and tamper-resistant audit storage. This prototype is not production-ready.

## Team contribution / authorship

Before final submission, list each actual team member and their true contribution. Do not claim work that was not completed.

## License

MIT — see `LICENSE`.

## Challenge reference

Hero Housing Fintech Challenge — E-Cell, IIT Bombay: https://unstop.com/hackathons/hero-housing-fintech-challenge-iit-bombay-1802169
