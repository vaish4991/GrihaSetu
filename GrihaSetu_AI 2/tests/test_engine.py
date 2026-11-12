import pytest

from core.engine import PolicyConfig, assess_application, calculate_emi


def test_emi_zero_interest():
    assert calculate_emi(120000, 0, 1) == pytest.approx(10000)


def test_emi_positive_and_reasonable():
    emi = calculate_emi(1_000_000, 8.5, 20)
    assert 8000 < emi < 9000


def test_balanced_case_routes_standard_review():
    result = assess_application(
        monthly_net_income=110000,
        existing_monthly_obligations=9000,
        property_value=5500000,
        requested_loan=4200000,
        annual_interest_rate=8.75,
        tenure_years=20,
        credit_score=742,
        months_in_current_job=30,
        payment_bounces_6m=0,
        documents={"identity": True, "income": True, "bank": True, "property": True},
        reviewer_flags={"identity_mismatch": False},
    )
    assert 0 < result["monthly_emi"]
    assert result["foir"] < 0.50
    assert result["ltv"] < 0.80
    assert result["review_route"] == "Standard review queue"
    assert "not an approval" in result["decision_notice"]


def test_missing_documents_and_exception_raise_review_intensity():
    result = assess_application(
        monthly_net_income=50000,
        existing_monthly_obligations=20000,
        property_value=3000000,
        requested_loan=2800000,
        annual_interest_rate=9.0,
        tenure_years=15,
        credit_score=640,
        months_in_current_job=3,
        payment_bounces_6m=3,
        documents={"identity": False, "income": False, "bank": True},
        reviewer_flags={"identity_mismatch": True},
    )
    assert result["review_route"] == "Priority manual review"
    assert result["review_signal_score"] < 40
    assert result["missing_documents"] == ["identity", "income"]


def test_invalid_income_is_rejected():
    with pytest.raises(ValueError):
        assess_application(
            monthly_net_income=0,
            existing_monthly_obligations=0,
            property_value=1,
            requested_loan=0,
        )


def test_custom_policy_is_applied():
    result = assess_application(
        monthly_net_income=80000,
        existing_monthly_obligations=10000,
        property_value=4000000,
        requested_loan=2500000,
        policy=PolicyConfig(max_foir=0.40, max_ltv=0.70, minimum_credit_score=720),
    )
    assert result["policy_assumptions"]["max_foir"] == 0.40
    assert result["policy_assumptions"]["max_ltv"] == 0.70
