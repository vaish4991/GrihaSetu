# GrihaSetu AI — 3-minute demo script

## Before the demo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local address printed by Streamlit, normally `http://localhost:8501`.

## Demo flow

### 1. Introduce the workflow (20 seconds)

"GrihaSetu AI is an end-to-end mortgage-underwriting workflow prototype. It maps to the eight requirements in the brief, from multi-source intake to explainable recommendations and audit export. All external sources shown are synthetic simulations."

### 2. Show a clean case (40 seconds)

- In the sidebar, select **Balanced — approve recommendation**.
- Click **Load selected scenario**.
- Check the Applicant, Data Sources, KYC & Fraud, Documents & Property and Compliance tabs.
- Click **Run end-to-end underwriting**.
- Show the EMI, FOIR, LTV, document readiness and risk signal points.
- Explain that the output is an **APPROVE RECOMMENDATION (DEMO RULES)**, not a sanction.

### 3. Show exception handling (45 seconds)

- Select **Evidence exception — refer recommendation** and load it.
- Run the workflow.
- Open **Decision explanation** and **Controls & checks**.
- Point out KYC review, income variance, missing property papers and title legal-review triggers.
- Explain why the system routes the case to **REFER FOR HUMAN REVIEW**.

### 4. Show policy decisioning (35 seconds)

- Select **Affordability breach — reject recommendation** and load it.
- Run the workflow.
- Explain the illustrative FOIR/LTV/score hard-band failures and the **REJECT RECOMMENDATION (DEMO RULES)** outcome.

### 5. Show governance and audit (30 seconds)

- Open **Data lineage**, **Controls & checks** and **Audit trail**.
- Download the CSV case summary and JSON audit bundle.
- Point to the policy version and reason codes.

## Honest scope statement

"The connectors are mock adapters with synthetic fixtures. KYC/AML, bank, bureau and property statuses are simulations; documents are availability checkboxes, not OCR or authentication. The risk logic is deterministic and explainable, not a trained ML model. The compliance gates are workflow controls, not a compliance certification. Live integrations and production governance are next steps."

## Do not claim

- Live API connectivity to banks, bureaus, KYC/AML services or property registries.
- Actual document verification, title search, fraud detection or AML screening.
- A probability of default or a trained ML model.
- Approval, sanction, loan offer, regulatory compliance or production readiness.
