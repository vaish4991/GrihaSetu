"""End-to-end, explainable mortgage-underwriting demo orchestration."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from core.engine import PolicyConfig, assess_application
from core.integrations import build_synthetic_data_bundle


PASS = "PASS"
REVIEW = "REVIEW"
BLOCK = "BLOCK"


def _event(case_id: str, event_type: str, detail: str) -> dict[str, str]:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "case_id": case_id,
        "event": event_type,
        "detail": detail,
        "actor": "GrihaSetu AI demo engine",
    }


def run_full_underwriting(
    *,
    case_id: str,
    monthly_net_income: float,
    existing_monthly_obligations: float,
    property_value: float,
    requested_loan: float,
    annual_interest_rate: float,
    tenure_years: int,
    credit_score: int,
    months_in_current_job: int,
    payment_bounces_6m: int,
    documents: Mapping[str, bool],
    reviewer_flags: Mapping[str, bool],
    bank_income_variance_pct: float,
    kyc_status: str,
    aml_status: str,
    property_title_status: str,
    compliance_controls: Mapping[str, bool],
    policy: PolicyConfig | None = None,
    loan_product: str = "Home Loan",
) -> dict[str, Any]:
    """Evaluate a synthetic end-to-end case and return a demo recommendation.

    Decision labels are simulated recommendations only. They are not a lender's
    approval, sanction, rejection, regulated KYC/AML result or compliance opinion.
    """
    policy = policy or PolicyConfig()
    if not case_id.strip():
        raise ValueError("Case ID is required.")
    if loan_product not in {"Home Loan", "Loan Against Property (LAP)"}:
        raise ValueError("Choose Home Loan or Loan Against Property (LAP).")
    if not -100 <= bank_income_variance_pct <= 100:
        raise ValueError("Bank income variance must be between -100% and 100%.")
    allowed_kyc = {"Matched", "Review required", "Not verified"}
    allowed_aml = {"No potential match", "Potential match", "Not screened"}
    allowed_title = {"Clear in demo", "Needs legal review", "Adverse marker"}
    if kyc_status not in allowed_kyc or aml_status not in allowed_aml:
        raise ValueError("Choose a valid KYC and AML demo status.")
    if property_title_status not in allowed_title:
        raise ValueError("Choose a valid property title demo status.")

    base = assess_application(
        monthly_net_income=monthly_net_income,
        existing_monthly_obligations=existing_monthly_obligations,
        property_value=property_value,
        requested_loan=requested_loan,
        annual_interest_rate=annual_interest_rate,
        tenure_years=tenure_years,
        credit_score=credit_score,
        months_in_current_job=months_in_current_job,
        payment_bounces_6m=payment_bounces_6m,
        documents=documents,
        reviewer_flags=reviewer_flags,
        policy=policy,
    )

    connector_bundle = build_synthetic_data_bundle(
        case_id=case_id,
        loan_product=loan_product,
        monthly_income=monthly_net_income,
        existing_obligations=existing_monthly_obligations,
        credit_score=credit_score,
        property_value=property_value,
        bank_income_variance_pct=bank_income_variance_pct,
        kyc_status=kyc_status,
        aml_status=aml_status,
        property_title_status=property_title_status,
    )

    checks: list[dict[str, str]] = []
    reasons: list[str] = list(base["reasons"])
    actions: list[str] = list(base["recommended_actions"])
    hard_policy_failures: list[str] = []
    critical_review_triggers: list[str] = []

    def add_check(name: str, status: str, observation: str, control: str) -> None:
        checks.append({"control": name, "status": status, "observation": observation, "demo_control": control})

    # 1. Data source integration checks: connector presence is simulated and explicit.
    add_check("Applicant intake", PASS, "Application input received", "Internal intake adapter")
    add_check("Bureau source", "SIMULATED", f"Mock score {credit_score} returned", "Synthetic bureau adapter; no live bureau pull")
    add_check("Bank source", "SIMULATED", f"Mock income variance {bank_income_variance_pct:.1f}%", "Synthetic bank adapter; no bank account accessed")
    add_check("Property source", "SIMULATED", f"Mock value ₹{property_value:,.0f}", "Synthetic property adapter; no registry query")

    # 2. Eligibility and policy checks.
    if base["foir"] > policy.max_foir:
        hard_policy_failures.append("FOIR exceeds the illustrative demo ceiling")
        add_check("FOIR affordability", BLOCK, f"{base['foir']:.1%} vs {policy.max_foir:.0%} demo ceiling", "Configurable demo policy")
    else:
        add_check("FOIR affordability", PASS, f"{base['foir']:.1%} within {policy.max_foir:.0%} demo ceiling", "Configurable demo policy")
    if base["ltv"] > policy.max_ltv:
        hard_policy_failures.append("LTV exceeds the illustrative demo ceiling")
        add_check("LTV collateral", BLOCK, f"{base['ltv']:.1%} vs {policy.max_ltv:.0%} demo ceiling", "Configurable demo policy")
    else:
        add_check("LTV collateral", PASS, f"{base['ltv']:.1%} within {policy.max_ltv:.0%} demo ceiling", "Configurable demo policy")
    if credit_score < 650:
        hard_policy_failures.append("Bureau score is below the illustrative demo hard-review band")
        add_check("Bureau policy band", BLOCK, f"Score {credit_score}; demo lower band is 650", "Illustrative score band; not lender policy")
    elif credit_score < policy.minimum_credit_score:
        critical_review_triggers.append("Bureau score falls below the demo standard threshold")
        add_check("Bureau policy band", REVIEW, f"Score {credit_score}; demo standard threshold is {policy.minimum_credit_score}", "Illustrative score band; manual review required")
    else:
        add_check("Bureau policy band", PASS, f"Score {credit_score} meets the demo threshold", "Illustrative score band; not lender policy")

    # 3. KYC/AML & fraud indicators.
    if kyc_status == "Matched":
        add_check("KYC identity status", PASS, "Synthetic identity-match response", "Mock KYC adapter; not identity verification")
    else:
        critical_review_triggers.append(f"KYC status: {kyc_status}")
        add_check("KYC identity status", REVIEW, kyc_status, "Manual verification required; no KYC vendor contacted")
    if aml_status == "No potential match":
        add_check("AML screening status", PASS, "Synthetic no-match response", "Mock AML adapter; not a live screening")
    else:
        critical_review_triggers.append(f"AML status: {aml_status}")
        add_check("AML screening status", REVIEW, aml_status, "Potential match / incomplete screen must be reviewed")
    fraud_flags = [name for name, active in reviewer_flags.items() if active]
    if fraud_flags:
        critical_review_triggers.append("One or more fraud/consistency exception flags are active")
        add_check("Fraud / consistency indicators", REVIEW, ", ".join(fraud_flags), "Rule-based synthetic exception flags; not ML fraud detection")
    else:
        add_check("Fraud / consistency indicators", PASS, "No demo exception flags activated", "No actual fraud screening performed")
    if abs(bank_income_variance_pct) > 20:
        critical_review_triggers.append("Bank-to-declared income variance exceeds 20% in the demo")
        add_check("Income consistency", REVIEW, f"{bank_income_variance_pct:.1f}% variance", "Illustrative exception threshold; verify source records")
    elif abs(bank_income_variance_pct) > 10:
        critical_review_triggers.append("Bank-to-declared income variance exceeds 10% in the demo")
        add_check("Income consistency", REVIEW, f"{bank_income_variance_pct:.1f}% variance", "Illustrative exception threshold; verify source records")
    else:
        add_check("Income consistency", PASS, f"{bank_income_variance_pct:.1f}% variance within demo tolerance", "Illustrative comparison; not a bank-data verification")

    # 4. Documents and property checks.
    missing_docs = base["missing_documents"]
    if missing_docs:
        critical_review_triggers.append("Required document categories are missing")
        add_check("Document completeness", REVIEW, ", ".join(missing_docs), "Availability checklist only; no upload/OCR/authentication")
    else:
        add_check("Document completeness", PASS, "All demo checklist categories marked available", "Availability checklist only; independent verification still required")
    if property_title_status == "Clear in demo":
        add_check("Property title status", PASS, "Synthetic clear status selected", "Mock property status; no legal/title search performed")
    else:
        critical_review_triggers.append(f"Property status: {property_title_status}")
        add_check("Property title status", REVIEW, property_title_status, "Refer to authorised legal/property due diligence")

    # 5. Compliance guardrail checks (demonstration gates, not legal certification).
    control_labels = {
        "credit_consent": "Credit-data consent captured",
        "privacy_notice": "Privacy notice acknowledged",
        "purpose_limitation": "Data-purpose limitation acknowledged",
        "fair_practices": "Fair-practices disclosure acknowledged",
    }
    for key, label in control_labels.items():
        passed = bool(compliance_controls.get(key, False))
        add_check(
            label,
            PASS if passed else REVIEW,
            "Acknowledged in demo" if passed else "Not acknowledged",
            "Demo workflow control only; not a legal compliance conclusion",
        )
        if not passed:
            critical_review_triggers.append(f"Required demo control incomplete: {label}")

    # Additional weighted signals from the integration and verification layers.
    # These points are explainable demo weights, not a calibrated credit-risk model.
    supplemental_risk_points = 0
    risk_components = [{"signal": "Core affordability / document / declared history rules", "points": base["review_points"]}]
    if kyc_status != "Matched":
        supplemental_risk_points += 15
        risk_components.append({"signal": "KYC status requires review", "points": 15})
    if aml_status == "Potential match":
        supplemental_risk_points += 25
        risk_components.append({"signal": "Potential AML match in synthetic response", "points": 25})
    elif aml_status == "Not screened":
        supplemental_risk_points += 12
        risk_components.append({"signal": "AML screening incomplete", "points": 12})
    if abs(bank_income_variance_pct) > 20:
        supplemental_risk_points += 15
        risk_components.append({"signal": "Bank / declared income variance above 20%", "points": 15})
    elif abs(bank_income_variance_pct) > 10:
        supplemental_risk_points += 8
        risk_components.append({"signal": "Bank / declared income variance above 10%", "points": 8})
    if property_title_status == "Adverse marker":
        supplemental_risk_points += 20
        risk_components.append({"signal": "Adverse property marker", "points": 20})
    elif property_title_status == "Needs legal review":
        supplemental_risk_points += 10
        risk_components.append({"signal": "Property title needs legal review", "points": 10})
    total_risk_signal_points = min(100, base["review_points"] + supplemental_risk_points)

    # 6. Instant outcome simulation. Critical controls take precedence over policy failures.
    if critical_review_triggers:
        recommendation = "REFER"
        recommendation_label = "REFER FOR HUMAN REVIEW"
        recommendation_reason = "One or more verification, evidence or governance controls require review."
        next_step = "Hold progression and assign the flagged controls to an authorised reviewer."
    elif hard_policy_failures:
        recommendation = "REJECT"
        recommendation_label = "REJECT RECOMMENDATION (DEMO RULES)"
        recommendation_reason = "A configured illustrative demo policy threshold was breached."
        next_step = "Show the policy reason, permit correction/appeal handling, and obtain human review before any real decision."
    elif base["review_points"] >= 30:
        recommendation = "REFER"
        recommendation_label = "REFER FOR HUMAN REVIEW"
        recommendation_reason = "The transparent review-signal rules raised the case for enhanced review."
        next_step = "Review the rule trace and supporting evidence before proceeding."
    else:
        recommendation = "APPROVE"
        recommendation_label = "APPROVE RECOMMENDATION (DEMO RULES)"
        recommendation_reason = "All configured demo controls passed and no review trigger was raised."
        next_step = "Present the complete case to an authorised credit officer; this is not a sanction or offer."

    if not reasons:
        reasons.append(recommendation_reason)
    if not actions:
        actions.append(next_step)
    reasons.extend(critical_review_triggers)
    reasons.extend(hard_policy_failures)

    # 7. Explainability and append-only-in-session audit events.
    audit = [
        _event(case_id, "APPLICATION_RECEIVED", f"Synthetic {loan_product} application details accepted by the demo UI."),
        _event(case_id, "DATA_SOURCES_AGGREGATED", "Five labelled synthetic connector records generated; no external APIs called."),
        _event(case_id, "AFFORDABILITY_EVALUATED", f"EMI ₹{base['monthly_emi']:,.0f}; FOIR {base['foir']:.1%}; LTV {base['ltv']:.1%}."),
        _event(case_id, "KYC_FRAUD_CONTROLS_EVALUATED", f"KYC {kyc_status}; AML {aml_status}; exception flags {len(fraud_flags)}."),
        _event(case_id, "DOCUMENT_PROPERTY_CONTROLS_EVALUATED", f"Missing document categories {len(missing_docs)}; property status {property_title_status}."),
        _event(case_id, "COMPLIANCE_GATES_EVALUATED", f"{sum(bool(v) for v in compliance_controls.values())}/{len(control_labels)} demo controls acknowledged."),
        _event(case_id, "DECISION_RECOMMENDATION_CREATED", f"{recommendation}: {recommendation_reason}"),
    ]

    return {
        "case_id": case_id,
        "loan_product": loan_product,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_assessment": base,
        "connector_bundle": connector_bundle,
        "control_checks": checks,
        "recommendation": recommendation,
        "recommendation_label": recommendation_label,
        "recommendation_reason": recommendation_reason,
        "next_step": next_step,
        "critical_review_triggers": critical_review_triggers,
        "hard_policy_failures": hard_policy_failures,
        "risk_signal_points": total_risk_signal_points,
        "risk_components": risk_components,
        "risk_signal_label": "Transparent rule points; not probability of default",
        "audit_events": audit,
        "decision_notice": (
            "SIMULATED DEMO RECOMMENDATION ONLY. Not an actual loan approval, rejection, sanction, "
            "KYC/AML finding, regulatory compliance opinion or offer of credit. All connectors use synthetic data."
        ),
        "policy_version": "DEMO-POLICY-1.0",
    }
