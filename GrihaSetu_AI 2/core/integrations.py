"""Synthetic connector adapters for the GrihaSetu AI hackathon demonstration.

All connector outputs are deterministic synthetic records. No external institution,
credit bureau, bank, KYC provider, AML service or property registry is contacted.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class ConnectorRecord:
    source_name: str
    source_type: str
    status: str
    reference_id: str
    data_summary: str
    simulated: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_synthetic_data_bundle(
    *,
    case_id: str,
    loan_product: str,
    monthly_income: float,
    existing_obligations: float,
    credit_score: int,
    property_value: float,
    bank_income_variance_pct: float,
    kyc_status: str,
    aml_status: str,
    property_title_status: str,
) -> dict[str, Any]:
    """Return a small multi-source bundle with explicit simulated provenance."""
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    ref = case_id.upper().replace(" ", "-")

    records = [
        ConnectorRecord(
            source_name="Applicant intake",
            source_type="Internal application form",
            status="RECEIVED",
            reference_id=f"INTAKE-{ref}",
            data_summary=(
                f"{loan_product}; synthetic household income ₹{monthly_income:,.0f}/month; "
                f"existing obligations ₹{existing_obligations:,.0f}/month"
            ),
        ),
        ConnectorRecord(
            source_name="Credit bureau adapter",
            source_type="Mock bureau response",
            status="SIMULATED RESPONSE",
            reference_id=f"BUREAU-{ref}",
            data_summary=f"Illustrative bureau score {credit_score}; not a bureau pull",
        ),
        ConnectorRecord(
            source_name="Bank statement adapter",
            source_type="Mock account-aggregator response",
            status="SIMULATED RESPONSE",
            reference_id=f"BANK-{ref}",
            data_summary=(
                f"Declared vs. sample verified income variance {bank_income_variance_pct:.1f}%; "
                "no bank account accessed"
            ),
        ),
        ConnectorRecord(
            source_name="Property registry adapter",
            source_type="Mock property record",
            status="SIMULATED RESPONSE",
            reference_id=f"PROPERTY-{ref}",
            data_summary=(
                f"Indicative value ₹{property_value:,.0f}; title status '{property_title_status}' "
                "is a scenario input, not a registry search"
            ),
        ),
        ConnectorRecord(
            source_name="KYC / AML screening adapter",
            source_type="Mock screening response",
            status="SIMULATED RESPONSE",
            reference_id=f"SCREEN-{ref}",
            data_summary=f"KYC: {kyc_status}; AML: {aml_status}; no live screening performed",
        ),
    ]
    return {
        "generated_at_utc": stamp,
        "case_id": case_id,
        "simulated": True,
        "records": [record.to_dict() for record in records],
    }
