"""
Mock data for engine unit tests.
Creates a fictional business state with known values for deterministic testing.
"""

from datetime import date, timedelta
from schemas import (
    BusinessState, Obligation, Receivable, CounterpartyProfile,
    ObligationType, Urgency, Flexibility, RelationshipType, TransactionType,
)

TODAY = date.today()


def get_mock_business_state() -> BusinessState:
    """Return a mock BusinessState for testing."""
    return BusinessState(
        business_name="Test Fashion Store",
        as_of_date=TODAY,
        cash_balance=150000.0,
        locked_cash=0.0,
        obligations=[
            Obligation(
                id="obl_supplier_a", counterparty_id="cp_supplier_a",
                counterparty_name="Supplier A", type=ObligationType.SUPPLIER,
                amount=45000, due_date=TODAY + timedelta(days=3),
                urgency=Urgency.HIGH, flexibility=Flexibility.MEDIUM,
                penalty_rate=1.6,
            ),
            Obligation(
                id="obl_electricity", counterparty_id="cp_electricity",
                counterparty_name="Electricity Board", type=ObligationType.UTILITY,
                amount=8000, due_date=TODAY + timedelta(days=7),
                urgency=Urgency.MEDIUM, flexibility=Flexibility.LOW,
                penalty_rate=1.8,
            ),
            Obligation(
                id="obl_salaries", counterparty_id="cp_employees",
                counterparty_name="Employee Salaries", type=ObligationType.SALARY,
                amount=90000, due_date=TODAY + timedelta(days=2),
                urgency=Urgency.HIGH, flexibility=Flexibility.LOW,
                penalty_rate=0.2,
            ),
            Obligation(
                id="obl_supplier_b", counterparty_id="cp_supplier_b",
                counterparty_name="Supplier B", type=ObligationType.SUPPLIER,
                amount=12000, due_date=TODAY + timedelta(days=14),
                urgency=Urgency.LOW, flexibility=Flexibility.HIGH,
                penalty_rate=1.0,
            ),
            Obligation(
                id="obl_rent", counterparty_id="cp_landlord",
                counterparty_name="Shop Rent", type=ObligationType.RENT,
                amount=35000, due_date=TODAY + timedelta(days=1),
                urgency=Urgency.CRITICAL, flexibility=Flexibility.LOW,
                penalty_rate=0.6,
            ),
        ],
        receivables=[
            Receivable(
                id="rec_meesho_payout", counterparty_id="cp_meesho",
                counterparty_name="Meesho Payout",
                amount=120000, expected_date=TODAY + timedelta(days=4),
                confidence=0.85,
            ),
            Receivable(
                id="rec_flipkart", counterparty_id="cp_flipkart",
                counterparty_name="Flipkart Settlement",
                amount=45000, expected_date=TODAY + timedelta(days=10),
                confidence=0.9,
            ),
        ],
        counterparties=[
            CounterpartyProfile(id="cp_supplier_a", name="Supplier A", relationship=RelationshipType.REGULAR_SUPPLIER, flexibility=Flexibility.MEDIUM),
            CounterpartyProfile(id="cp_electricity", name="Electricity Board", relationship=RelationshipType.UTILITY_PROVIDER, flexibility=Flexibility.LOW),
            CounterpartyProfile(id="cp_employees", name="Employee Salaries", relationship=RelationshipType.EMPLOYEE, flexibility=Flexibility.LOW, communication_tone="friendly"),
            CounterpartyProfile(id="cp_supplier_b", name="Supplier B", relationship=RelationshipType.REGULAR_SUPPLIER, flexibility=Flexibility.HIGH),
            CounterpartyProfile(id="cp_landlord", name="Shop Rent", relationship=RelationshipType.LANDLORD, flexibility=Flexibility.LOW),
        ],
        gst_registered=True,
    )


def get_mock_payment_history() -> dict:
    return {
        "total_obligations_last_90_days": 10,
        "paid_on_time": 7,
        "paid_late": 2,
        "missed": 1,
        "gst_filings_due_last_90_days": 6,
        "gst_filed_on_time": 6,
        "average_receivable_delay_days": 3,
    }
