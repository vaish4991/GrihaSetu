"""Transparent, illustrative mortgage pre-screening rules for the GrihaSetu AI demo.

This is a hackathon prototype, not a lender policy, credit bureau model, or loan decision.
All thresholds are configurable assumptions and every case requires human review.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping


@dataclass(frozen=True)
class PolicyConfig:
    max_foir: float = 0.50          # illustrative total-obligation / net-income ceiling
    max_ltv: float = 0.80           # illustrative loan / property-value ceiling
    minimum_credit_score: int = 700
    standard_interest_rate: float = 8.75


def calculate_emi(principal: float, annual_rate: float, tenure_years: int) -> float:
    """Calculate monthly reducing-balance EMI in rupees."""
    if principal < 0:
        raise ValueError("Principal cannot be negative.")
    if annual_rate < 0:
        raise ValueError("Annual interest rate cannot be negative.")
    if tenure_years <= 0:
        raise ValueError("Tenure must be greater than zero.")
    if principal == 0:
        return 0.0
    months = tenure_years * 12
    monthly_rate = annual_rate / 1200
    if monthly_rate == 0:
        return principal / months
    factor = (1 + monthly_rate) ** months
    return principal * monthly_rate * factor / (factor - 1)


def _loan_from_emi(max_monthly_emi: float, annual_rate: float, tenure_years: int) -> float:
    """Reverse the EMI formula to estimate principal supported by an EMI."""
    if max_monthly_emi <= 0:
        return 0.0
    months = tenure_years * 12
    monthly_rate = annual_rate / 1200
    if monthly_rate == 0:
        return max_monthly_emi * months
    factor = (1 + monthly_rate) ** months
    return max_monthly_emi * (factor - 1) / (monthly_rate * factor)


def assess_application(
    *,
    monthly_net_income: float,
    existing_monthly_obligations: float,
    property_value: float,
    requested_loan: float,
    annual_interest_rate: float = 8.75,
    tenure_years: int = 20,
    credit_score: int = 730,
    months_in_current_job: int = 24,
    payment_bounces_6m: int = 0,
    documents: Mapping[str, bool] | None = None,
    reviewer_flags: Mapping[str, bool] | None = None,
    policy: PolicyConfig | None = None,
) -> dict:
    """Return explainable pre-screen metrics and a human-review route.

    `documents` and `reviewer_flags` are booleans supplied by the demo user/reviewer.
    The prototype does not OCR, authenticate documents, contact bureaus, or detect fraud.
    """
    policy = policy or PolicyConfig()
    documents = dict(documents or {})
    reviewer_flags = dict(reviewer_flags or {})

    if monthly_net_income <= 0:
        raise ValueError("Monthly net income must be greater than zero.")
    if existing_monthly_obligations < 0 or property_value <= 0 or requested_loan < 0:
        raise ValueError("Obligations and loan cannot be negative; property value must be positive.")
    if payment_bounces_6m < 0 or months_in_current_job < 0:
        raise ValueError("Employment months and payment bounces cannot be negative.")
    if not 0 <= policy.max_foir <= 1 or not 0 < policy.max_ltv <= 1:
        raise ValueError("Policy limits must be expressed as valid ratios.")

    emi = calculate_emi(requested_loan, annual_interest_rate, tenure_years)
    total_monthly_obligations = existing_monthly_obligations + emi
    foir = total_monthly_obligations / monthly_net_income
    ltv = requested_loan / property_value
    missing_documents = [name for name, present in documents.items() if not present]
    document_readiness = 100.0 if not documents else 100.0 * (len(documents) - len(missing_documents)) / len(documents)

    # Transparent review-signal points. These are NOT a probability of default.
    points = 0
    reasons: list[str] = []
    actions: list[str] = []

    if foir > policy.max_foir:
        points += 30
        reasons.append(f"FOIR is {foir:.1%}, above the illustrative {policy.max_foir:.0%} ceiling.")
        actions.append("Rework the requested loan amount or verify whether additional documented income can be considered.")
    elif foir > policy.max_foir * 0.80:
        points += 15
        reasons.append(f"FOIR is {foir:.1%}, close to the illustrative affordability ceiling.")
        actions.append("Review monthly obligations and income stability before progressing.")

    if ltv > policy.max_ltv:
        points += 25
        reasons.append(f"LTV is {ltv:.1%}, above the illustrative {policy.max_ltv:.0%} ceiling.")
        actions.append("Review the requested loan against the property value and applicable lender policy.")
    elif ltv > policy.max_ltv * 0.93:
        points += 10
        reasons.append(f"LTV is {ltv:.1%}, close to the illustrative collateral limit.")
        actions.append("Confirm property valuation and applicable collateral policy.")

    if credit_score < 650:
        points += 25
        reasons.append("Bureau score is below the demo's lower review band.")
        actions.append("Request an authorised bureau review and investigate any disputed records.")
    elif credit_score < policy.minimum_credit_score:
        points += 15
        reasons.append("Bureau score is below the demo's standard review threshold.")
        actions.append("Route for manual credit assessment; do not auto-decline.")

    if months_in_current_job < 6:
        points += 15
        reasons.append("Current employment tenure is under six months.")
        actions.append("Verify employment continuity and acceptable income evidence.")
    elif months_in_current_job < 12:
        points += 8
        reasons.append("Current employment tenure is under twelve months.")
        actions.append("Review employment history and income continuity.")

    if payment_bounces_6m >= 3:
        points += 20
        reasons.append("Three or more payment bounces were declared for the last six months.")
        actions.append("Request an explanation and verify the underlying bank-statement entries.")
    elif payment_bounces_6m > 0:
        points += 10
        reasons.append("Payment bounce(s) were declared for the last six months.")
        actions.append("Review the reason and recency of the declared payment bounce(s).")

    if missing_documents:
        points += min(20, 5 * len(missing_documents))
        reasons.append("One or more required document categories are marked as not available.")
        actions.append("Collect and verify the missing document categories before underwriting.")

    active_flags = [name for name, active in reviewer_flags.items() if active]
    if active_flags:
        points += min(40, 20 * len(active_flags))
        labels = ", ".join(name.replace("_", " ") for name in active_flags)
        reasons.append(f"Reviewer-entered exception flag(s): {labels}.")
        actions.append("Escalate the exception(s) for independent verification and preserve an audit trail.")

    points = min(points, 100)
    readiness_score = max(0, 100 - points)
    if points >= 60:
        route = "Priority manual review"
    elif points >= 30:
        route = "Enhanced manual review"
    else:
        route = "Standard review queue"

    available_emi_capacity = max(0.0, monthly_net_income * policy.max_foir - existing_monthly_obligations)
    foir_supported_loan = _loan_from_emi(available_emi_capacity, annual_interest_rate, tenure_years)
    ltv_supported_loan = property_value * policy.max_ltv
    indicative_fit_cap = min(foir_supported_loan, ltv_supported_loan)

    if not reasons:
        reasons.append("No review trigger was raised by the demo rules for the supplied inputs.")
        actions.append("Continue with official KYC, bureau, property, legal and credit checks under lender policy.")

    return {
        "monthly_emi": round(emi, 2),
        "total_monthly_obligations": round(total_monthly_obligations, 2),
        "foir": round(foir, 4),
        "ltv": round(ltv, 4),
        "document_readiness": round(document_readiness, 1),
        "missing_documents": missing_documents,
        "review_signal_score": readiness_score,
        "review_points": points,
        "review_route": route,
        "indicative_fit_cap": round(indicative_fit_cap, 2),
        "foir_supported_loan": round(foir_supported_loan, 2),
        "ltv_supported_loan": round(ltv_supported_loan, 2),
        "reasons": reasons,
        "recommended_actions": actions,
        "active_reviewer_flags": active_flags,
        "policy_assumptions": asdict(policy),
        "decision_notice": "Pre-screen only — not an approval, rejection, sanction, or offer of credit. Human review is mandatory.",
    }
