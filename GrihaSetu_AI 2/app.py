from __future__ import annotations

import json
import pandas as pd
import streamlit as st

from core.demo import DEMO_SCENARIOS
from core.engine import PolicyConfig
from core.underwriting import run_full_underwriting

st.set_page_config(page_title="GrihaSetu AI | Mortgage Underwriting", page_icon="🏡", layout="wide")

st.markdown(
    """
    <style>
    :root { --ink:#172033; --muted:#68758b; --line:#e6eaf0; --accent:#0c8b76; }
    .block-container { padding-top: 1.2rem; max-width: 1450px; }
    .hero { background: linear-gradient(120deg,#102b3a 0%,#145b58 58%,#1c8d78 100%); padding: 1.55rem 1.8rem; border-radius: 18px; color: white; margin-bottom: 1rem; }
    .hero h1 { color: white; margin: 0; font-size: 2.25rem; letter-spacing: -.04em; }
    .hero p { color: #d6eee9; margin: .35rem 0 0 0; font-size: 1rem; }
    .notice { background:#fff8e8; border:1px solid #f3dfa9; border-radius:12px; padding: .85rem 1rem; color:#6a4b0c; font-size:.9rem; }
    .small-note { color:#68758b; font-size:.86rem; }
    div[data-testid="stMetric"] { background:#fff; border:1px solid #e6eaf0; padding:12px 14px; border-radius:14px; }
    </style>
    <div class="hero">
      <div style="font-size:.76rem;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:#b6e7dc">Hero Housing Fintech Challenge · Problem Statement 02</div>
      <h1>GrihaSetu AI</h1>
      <p>End-to-end explainable mortgage underwriting workflow — from application intake to a traceable demo recommendation.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "HACKATHON DEMO ONLY · All external data sources and KYC/AML responses are synthetic simulations. "
    "This app does not contact a bank, bureau, registry or screening provider, and does not make a real lending decision."
)

SCENARIO_NAMES = list(DEMO_SCENARIOS)
if "scenario_values" not in st.session_state:
    st.session_state["scenario_values"] = DEMO_SCENARIOS[SCENARIO_NAMES[0]].copy()

with st.sidebar:
    st.markdown("## Demo controls")
    selected_scenario = st.selectbox("Load a repeatable demo scenario", SCENARIO_NAMES, index=0)
    if st.button("Load selected scenario", use_container_width=True):
        st.session_state["scenario_values"] = DEMO_SCENARIOS[selected_scenario].copy()
        st.session_state.pop("last_result", None)
        # Clear widget state so the selected scenario repopulates every field.
        for widget_key in [
            "case_id", "monthly_income", "existing_obligations", "loan_type", "requested_loan",
            "tenure", "property_value", "interest_rate", "credit_score", "months_job", "bounces",
            "bank_income_variance", "kyc_status", "aml_status", "identity_mismatch",
            "bank_entry_exception", "employer_mismatch", "property_title_status",
            "credit_consent", "privacy_notice", "purpose_limitation", "fair_practices",
            "doc_0", "doc_1", "doc_2", "doc_3", "doc_4", "doc_5",
        ]:
            st.session_state.pop(widget_key, None)
        st.rerun()
    st.caption("Use synthetic cases only. The three scenarios demonstrate approve, refer and reject recommendations.")
    st.divider()
    st.markdown("### Illustrative policy settings")
    st.caption("These are configurable demo assumptions, not Hero Housing Finance policy or regulatory limits.")
    max_foir = st.slider("Maximum FOIR", 30, 70, 50, 1) / 100
    max_ltv = st.slider("Maximum LTV", 50, 90, 80, 1) / 100
    minimum_score = st.slider("Standard bureau review threshold", 600, 780, 700, 5)
    st.divider()
    st.markdown("### Data protection in this demo")
    st.caption("Do not enter PAN, Aadhaar, bank-account numbers, passwords or real customer documents. Data is processed in the current app session only.")

case = st.session_state["scenario_values"]

st.markdown("### End-to-end workflow")
flow_cols = st.columns(8)
flow_steps = ["1 Intake", "2 Data", "3 Eligibility", "4 KYC / AML", "5 Risk", "6 Property", "7 Compliance", "8 Decision + audit"]
for col, label in zip(flow_cols, flow_steps):
    with col:
        st.markdown(
            f"<div style='background:#edf3f7;border:1px solid #dce5ec;border-radius:9px;padding:9px 5px;text-align:center;font-size:.78rem;font-weight:650;color:#19334b'>{label}</div>",
            unsafe_allow_html=True,
        )

app_tab, source_tab, fraud_tab, property_tab, compliance_tab = st.tabs(
    ["1 · Applicant & loan", "2 · Data sources", "3 · KYC & fraud", "4 · Documents & property", "5 · Compliance controls"]
)

with app_tab:
    st.markdown("#### Applicant and loan application")
    st.caption("The case ID and financial details below are synthetic demo inputs.")
    a1, a2, a3 = st.columns(3)
    with a1:
        case_id = st.text_input("Synthetic case ID", value=case["case_id"], key="case_id")
        monthly_income = st.number_input("Net monthly household income (₹)", min_value=1, value=int(case["monthly_net_income"]), step=5000, key="monthly_income")
        existing_obligations = st.number_input("Existing monthly obligations / EMIs (₹)", min_value=0, value=int(case["existing_monthly_obligations"]), step=1000, key="existing_obligations")
    with a2:
        loan_type = st.selectbox("Loan product", ["Home Loan", "Loan Against Property (LAP)"], key="loan_type")
        requested_loan = st.number_input("Requested loan amount (₹)", min_value=0, value=int(case["requested_loan"]), step=100000, key="requested_loan")
        tenure = st.slider("Tenure (years)", 1, 30, int(case["tenure_years"]), key="tenure")
    with a3:
        property_value = st.number_input("Indicative property value (₹)", min_value=1, value=int(case["property_value"]), step=100000, key="property_value")
        interest_rate = st.number_input("Illustrative annual interest rate (%)", min_value=0.0, max_value=30.0, value=float(case["annual_interest_rate"]), step=0.25, key="interest_rate")
        credit_score = st.slider("Synthetic bureau score", 300, 900, int(case["credit_score"]), key="credit_score")
    months_job = st.number_input("Months in current employment / business", min_value=0, value=int(case["months_in_current_job"]), step=1, key="months_job")
    bounces = st.number_input("Declared payment bounces in last six months", min_value=0, max_value=12, value=int(case["payment_bounces_6m"]), step=1, key="bounces")

with source_tab:
    st.markdown("#### Multi-source data aggregation")
    st.info("These adapter cards demonstrate where external information enters the workflow. They return synthetic fixtures; no real API, bank, bureau or registry is connected.")
    st.dataframe(
        pd.DataFrame(
            [
                {"Source adapter": "Applicant intake", "Demo data returned": "Applicant and loan form fields", "Integration status": "Internal demo form"},
                {"Source adapter": "Credit bureau", "Demo data returned": "Synthetic bureau score", "Integration status": "Mock adapter — no bureau pull"},
                {"Source adapter": "Bank / account aggregator", "Demo data returned": "Synthetic income and obligation comparison", "Integration status": "Mock adapter — no account access"},
                {"Source adapter": "Property registry", "Demo data returned": "Synthetic property value and title status", "Integration status": "Mock adapter — no registry search"},
                {"Source adapter": "KYC / AML screening", "Demo data returned": "Selected synthetic KYC and AML response", "Integration status": "Mock adapter — no live screening"},
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
    bank_income_variance = st.slider("Synthetic bank-vs-declared income variance (%)", -50, 50, int(case["bank_income_variance_pct"]), 1, key="bank_income_variance")
    st.caption("A non-zero variance is an exception signal for the demonstration. It does not mean bank data has been fetched or verified.")

with fraud_tab:
    st.markdown("#### KYC, AML and fraud / consistency controls")
    f1, f2 = st.columns(2)
    with f1:
        kyc_status = st.selectbox("Synthetic KYC adapter response", ["Matched", "Review required", "Not verified"], index=["Matched", "Review required", "Not verified"].index(case["kyc_status"]), key="kyc_status")
        aml_status = st.selectbox("Synthetic AML screening response", ["No potential match", "Potential match", "Not screened"], index=["No potential match", "Potential match", "Not screened"].index(case["aml_status"]), key="aml_status")
    with f2:
        st.caption("Manual exception toggles simulate inconsistency signals. They do not detect fraud automatically.")
        identity_mismatch = st.checkbox("Identity details mismatch", value=bool(case["reviewer_flags"]["identity_mismatch"]), key="identity_mismatch")
        bank_entry_exception = st.checkbox("Unusual bank-entry pattern reported", value=bool(case["reviewer_flags"]["bank_entry_exception"]), key="bank_entry_exception")
        employer_mismatch = st.checkbox("Employer / income detail mismatch", value=bool(case["reviewer_flags"]["employer_mismatch"]), key="employer_mismatch")

with property_tab:
    st.markdown("#### Digital document-readiness and property review")
    st.caption("The checklist records availability/status only. No file upload, OCR, signature validation, title search or encumbrance search is performed.")
    doc_defaults = case["documents"]
    dcols = st.columns(3)
    doc_keys = ["Identity proof", "Income proof", "Bank statements", "Property papers", "Credit consent", "Property tax / encumbrance evidence"]
    docs = {}
    for idx, label in enumerate(doc_keys):
        with dcols[idx % 3]:
            default_value = doc_defaults.get(label, True)
            docs[label] = st.checkbox(f"{label} available", value=bool(default_value), key=f"doc_{idx}")
    property_title_status = st.selectbox(
        "Synthetic property title / legal status",
        ["Clear in demo", "Needs legal review", "Adverse marker"],
        index=["Clear in demo", "Needs legal review", "Adverse marker"].index(case["property_title_status"]),
        key="property_title_status",
    )

with compliance_tab:
    st.markdown("#### Compliance and governance gates")
    st.warning("These are workflow acknowledgements and guardrails for the prototype. They are not legal advice, a regulatory mapping, or certification of compliance with NHB / RBI / Fair Practices requirements.")
    cc = case["compliance_controls"]
    compliance_controls = {
        "credit_consent": st.checkbox("Credit-data consent captured (demo acknowledgement)", value=bool(cc["credit_consent"]), key="credit_consent"),
        "privacy_notice": st.checkbox("Privacy notice acknowledged", value=bool(cc["privacy_notice"]), key="privacy_notice"),
        "purpose_limitation": st.checkbox("Data-purpose limitation acknowledged", value=bool(cc["purpose_limitation"]), key="purpose_limitation"),
        "fair_practices": st.checkbox("Fair-practices disclosure acknowledged", value=bool(cc["fair_practices"]), key="fair_practices"),
    }
    st.caption("An incomplete demo control routes the case to human review. A production implementation requires legal/compliance review and approved lender policy.")

st.divider()
run_clicked = st.button("Run end-to-end underwriting", type="primary", use_container_width=True)
if run_clicked:
    policy = PolicyConfig(
        max_foir=max_foir,
        max_ltv=max_ltv,
        minimum_credit_score=minimum_score,
        standard_interest_rate=float(interest_rate),
    )
    reviewer_flags = {
        "identity_mismatch": identity_mismatch,
        "bank_entry_exception": bank_entry_exception,
        "employer_mismatch": employer_mismatch,
    }
    try:
        result = run_full_underwriting(
            case_id=case_id.strip(),
            loan_product=loan_type,
            monthly_net_income=monthly_income,
            existing_monthly_obligations=existing_obligations,
            property_value=property_value,
            requested_loan=requested_loan,
            annual_interest_rate=interest_rate,
            tenure_years=tenure,
            credit_score=credit_score,
            months_in_current_job=months_job,
            payment_bounces_6m=bounces,
            documents=docs,
            reviewer_flags=reviewer_flags,
            bank_income_variance_pct=bank_income_variance,
            kyc_status=kyc_status,
            aml_status=aml_status,
            property_title_status=property_title_status,
            compliance_controls=compliance_controls,
            policy=policy,
        )
        st.session_state["last_result"] = result
        st.session_state["last_loan_type"] = loan_type
    except ValueError as exc:
        st.error(str(exc))

result = st.session_state.get("last_result")
if result:
    base = result["base_assessment"]
    st.divider()
    st.markdown("## Underwriting result")
    outcome = result["recommendation"]
    if outcome == "APPROVE":
        st.success(f"{result['recommendation_label']} — {result['recommendation_reason']}")
    elif outcome == "REJECT":
        st.error(f"{result['recommendation_label']} — {result['recommendation_reason']}")
    else:
        st.warning(f"{result['recommendation_label']} — {result['recommendation_reason']}")
    st.markdown(f"<div class='notice'><b>Guardrail:</b> {result['decision_notice']}</div>", unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Indicative EMI", f"₹{base['monthly_emi']:,.0f}")
    with m2:
        st.metric("FOIR", f"{base['foir']:.1%}")
    with m3:
        st.metric("LTV", f"{base['ltv']:.1%}")
    with m4:
        st.metric("Document readiness", f"{base['document_readiness']:.0f}%")
    with m5:
        st.metric("Risk signal points", f"{result['risk_signal_points']}/100", help=result["risk_signal_label"])

    rtab1, rtab2, rtab3, rtab4 = st.tabs(["Decision explanation", "Data lineage", "Controls & checks", "Audit trail"])
    with rtab1:
        left, right = st.columns(2)
        with left:
            st.markdown("### Affordability and collateral")
            st.progress(min(1.0, base["foir"] / max_foir), text=f"FOIR: {base['foir']:.1%} / {max_foir:.0%} illustrative ceiling")
            st.progress(min(1.0, base["ltv"] / max_ltv), text=f"LTV: {base['ltv']:.1%} / {max_ltv:.0%} illustrative ceiling")
            st.metric("Indicative fit cap", f"₹{base['indicative_fit_cap']/100000:.2f} lakh")
            st.caption("Fit-cap math is an illustrative pre-screen calculation, not an eligibility promise.")
        with right:
            st.markdown("### Why the engine reached this route")
            for reason in result["critical_review_triggers"] + result["hard_policy_failures"] + base["reasons"]:
                st.write(f"• {reason}")
            if not result["critical_review_triggers"] and not result["hard_policy_failures"] and not base["reasons"]:
                st.write("• No demo rules raised a review trigger.")
        st.markdown("### Next recommended action")
        st.info(result["next_step"])
        st.markdown("### Decision governance")
        st.write("The output is a simulated recommendation for **" + result["loan_product"] + "**, generated from policy version **" + result["policy_version"] + "**. A real lender decision requires authorised policy, verified data, governance and human/legal controls.")
        st.markdown("### Risk-signal breakdown")
        st.dataframe(pd.DataFrame(result["risk_components"]), use_container_width=True, hide_index=True)


    with rtab2:
        st.markdown("### Synthetic connector responses")
        connector_df = pd.DataFrame(result["connector_bundle"]["records"])
        st.dataframe(connector_df, use_container_width=True, hide_index=True)
        st.caption("Each record carries simulated=True. This is a connector demonstration, not a live third-party integration.")

    with rtab3:
        st.markdown("### Eight-point challenge coverage")
        coverage_rows = [
            ("1. Multiple data sources", "Five labelled synthetic connector adapters"),
            ("2. Eligibility and policy", "EMI, FOIR, LTV and configurable illustrative thresholds"),
            ("3. Fraud detection and KYC/AML", "Mock screening responses plus explainable exception flags"),
            ("4. Risk scoring", "Deterministic rule points with visible reason codes; not ML"),
            ("5. Documents and property", "Availability checklist and simulated title-status routing"),
            ("6. Compliance checks", "Consent, privacy, purpose and fair-practices demo gates"),
            ("7. Instant decisioning", "Approve / reject / refer demo recommendations"),
            ("8. Explainability and governance", "Control trace, policy version, audit events and exports"),
        ]
        st.dataframe(pd.DataFrame(coverage_rows, columns=["Requirement", "What this prototype demonstrates"]), use_container_width=True, hide_index=True)
        st.markdown("### Control-by-control result")
        st.dataframe(pd.DataFrame(result["control_checks"]), use_container_width=True, hide_index=True)

    with rtab4:
        st.markdown("### Case audit events")
        st.dataframe(pd.DataFrame(result["audit_events"]), use_container_width=True, hide_index=True)
        st.caption("Audit events are kept in this active Streamlit session and exported for demonstration. This is not a tamper-proof production audit system.")

    summary = {
        "case_id": result["case_id"],
        "loan_product": result["loan_product"],
        "recommendation": result["recommendation"],
        "recommendation_label": result["recommendation_label"],
        "emi_inr": base["monthly_emi"],
        "foir_pct": round(base["foir"] * 100, 2),
        "ltv_pct": round(base["ltv"] * 100, 2),
        "document_readiness_pct": base["document_readiness"],
        "risk_signal_points": result["risk_signal_points"],
        "policy_version": result["policy_version"],
        "generated_at_utc": result["generated_at_utc"],
        "notice": result["decision_notice"],
    }
    exp1, exp2 = st.columns(2)
    with exp1:
        st.download_button("Download case summary (CSV)", pd.DataFrame([summary]).to_csv(index=False), file_name=f"{result['case_id']}_summary.csv", mime="text/csv", use_container_width=True)
    with exp2:
        st.download_button("Download audit bundle (JSON)", json.dumps(result, indent=2), file_name=f"{result['case_id']}_audit.json", mime="application/json", use_container_width=True)
else:
    st.info("Choose a demo scenario in the sidebar, review the five workflow tabs, and click **Run end-to-end underwriting** to generate a recommendation and audit trail.")

st.divider()
st.markdown("### Responsible-use boundary")
st.write(
    "GrihaSetu AI is a hackathon prototype. It uses synthetic source adapters, illustrative rules and scenario inputs. "
    "It does not connect to real credit bureaus, banks, account aggregators, KYC/AML providers or property registries; "
    "does not perform document OCR or authentication; does not use a trained ML model; and does not certify NHB/RBI/Fair Practices compliance. "
    "Approve / reject / refer labels are simulated recommendations only, not a sanction, offer or final credit decision."
)
st.caption("Python · Streamlit · Pandas · pytest · GitLab CI · Synthetic data only")
