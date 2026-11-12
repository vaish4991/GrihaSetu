from core.demo import DEMO_SCENARIOS
from core.engine import PolicyConfig
from core.underwriting import run_full_underwriting


def evaluate(scenario_name: str):
    scenario = DEMO_SCENARIOS[scenario_name]
    return run_full_underwriting(
        **scenario,
        policy=PolicyConfig(max_foir=0.50, max_ltv=0.80, minimum_credit_score=700),
    )


def test_balanced_scenario_produces_approve_recommendation():
    result = evaluate("Balanced — approve recommendation")
    assert result["recommendation"] == "APPROVE"
    assert len(result["connector_bundle"]["records"]) == 5
    assert all(record["simulated"] for record in result["connector_bundle"]["records"])
    assert len(result["audit_events"]) == 7


def test_evidence_exception_scenario_routes_to_refer():
    result = evaluate("Evidence exception — refer recommendation")
    assert result["recommendation"] == "REFER"
    assert result["critical_review_triggers"]
    assert any(row["control"] == "KYC identity status" and row["status"] == "REVIEW" for row in result["control_checks"])


def test_affordability_breach_scenario_produces_reject_recommendation():
    result = evaluate("Affordability breach — reject recommendation")
    assert result["recommendation"] == "REJECT"
    assert result["hard_policy_failures"]
    assert "SIMULATED DEMO RECOMMENDATION ONLY" in result["decision_notice"]


def test_missing_consent_routes_to_refer_even_when_policy_passes():
    scenario = DEMO_SCENARIOS["Balanced — approve recommendation"].copy()
    scenario["compliance_controls"] = dict(scenario["compliance_controls"])
    scenario["compliance_controls"]["credit_consent"] = False
    result = run_full_underwriting(**scenario)
    assert result["recommendation"] == "REFER"
    assert any("Credit-data consent" in trigger for trigger in result["critical_review_triggers"])


def test_large_bank_variance_routes_to_refer():
    scenario = DEMO_SCENARIOS["Balanced — approve recommendation"].copy()
    scenario["bank_income_variance_pct"] = 25
    result = run_full_underwriting(**scenario)
    assert result["recommendation"] == "REFER"
    assert any("income variance" in trigger for trigger in result["critical_review_triggers"])
