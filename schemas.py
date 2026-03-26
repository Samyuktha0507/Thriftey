"""
Thriftey Financial Engine — Unified Data Schema
All Pydantic models used across the system.
Every computed metric traces back to these structures.
"""

from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────

class ObligationType(str, Enum):
    SUPPLIER = "supplier"
    RENT = "rent"
    SALARY = "salary"
    UTILITY = "utility"
    LOAN_EMI = "loan_emi"
    TAX = "tax"
    GST = "gst"
    INSURANCE = "insurance"
    OTHER = "other"


class Urgency(str, Enum):
    CRITICAL = "critical"      # overdue or due today
    HIGH = "high"              # due within 3 days
    MEDIUM = "medium"          # due within 7 days
    LOW = "low"                # due beyond 7 days


class Flexibility(str, Enum):
    NONE = "none"              # no negotiation possible (tax, EMI)
    LOW = "low"                # slight flexibility (utility — late fee)
    MEDIUM = "medium"          # can negotiate 7-14 day extension
    HIGH = "high"              # very flexible (friendly supplier)


class RelationshipType(str, Enum):
    CRITICAL_SUPPLIER = "critical_supplier"
    REGULAR_SUPPLIER = "regular_supplier"
    UTILITY_PROVIDER = "utility_provider"
    EMPLOYEE = "employee"
    GOVERNMENT = "government"
    LENDER = "lender"
    LANDLORD = "landlord"
    OTHER = "other"


class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


# ── Core Data Models ────────────────────────────────────────────────────

class CounterpartyProfile(BaseModel):
    id: str
    name: str
    relationship: RelationshipType
    flexibility: Flexibility
    communication_tone: str = "professional"
    notes: str = ""


class Transaction(BaseModel):
    id: str
    date: date
    amount: float
    type: TransactionType
    description: str
    counterparty_id: Optional[str] = None
    source: str = "manual"


class Obligation(BaseModel):
    id: str
    counterparty_id: str
    counterparty_name: str
    type: ObligationType
    amount: float
    due_date: date
    urgency: Urgency = Urgency.MEDIUM
    flexibility: Flexibility = Flexibility.MEDIUM
    penalty_rate: float = 0.0
    penalty_fixed: float = 0.0
    is_recurring: bool = False
    notes: str = ""


class Receivable(BaseModel):
    id: str
    counterparty_id: str
    counterparty_name: str
    amount: float
    expected_date: date
    confidence: float = 0.8
    notes: str = ""


class BusinessState(BaseModel):
    business_name: str
    as_of_date: date
    cash_balance: float
    locked_cash: float = 0.0
    obligations: list[Obligation] = Field(default_factory=list)
    receivables: list[Receivable] = Field(default_factory=list)
    counterparties: list[CounterpartyProfile] = Field(default_factory=list)
    recent_transactions: list[Transaction] = Field(default_factory=list)
    gst_registered: bool = True
    is_composition_scheme: bool = False


# ── Output Models ────────────────────────────────────────────────────────

class DailySnapshot(BaseModel):
    day: date
    opening_balance: float
    inflows: float
    outflows: float
    closing_balance: float
    obligations_due: list[str] = Field(default_factory=list)
    receivables_due: list[str] = Field(default_factory=list)


class LiquiditySummary(BaseModel):
    cash_balance: float
    available_cash: float
    total_payables: float
    total_receivables: float
    net_position: float
    days_to_zero: int          # -1 means solvent beyond projection horizon
    runway: list[DailySnapshot] = Field(default_factory=list)


class ScoredObligation(BaseModel):
    obligation: Obligation
    priority_score: float
    urgency_contribution: float
    penalty_contribution: float
    relationship_contribution: float
    flexibility_contribution: float
    rank: int = 0
    can_pay: str = "unknown"
    cumulative_cash_after: float = 0.0


class ConstraintReport(BaseModel):
    available_cash: float
    total_obligations: float
    shortfall: float
    scored_obligations: list[ScoredObligation] = Field(default_factory=list)
    payable_obligations: list[str] = Field(default_factory=list)
    conflict_obligations: list[str] = Field(default_factory=list)
    is_constrained: bool = False


class ExplanationStep(BaseModel):
    obligation_id: str
    obligation_name: str
    decision: str
    cash_constraint: str
    risk_comparison: str
    tradeoff_justification: str


class WhatIfScenario(BaseModel):
    description: str
    delayed_receivable_id: Optional[str] = None
    delayed_receivable_new_date: Optional[date] = None
    removed_obligation_id: Optional[str] = None
    added_obligation: Optional[Obligation] = None
    changed_obligation_id: Optional[str] = None
    changed_obligation_amount: Optional[float] = None
    changed_obligation_date: Optional[date] = None
    cash_balance_override: Optional[float] = None


class WhatIfResult(BaseModel):
    scenario_description: str
    original_days_to_zero: int
    new_days_to_zero: int
    delta_days: int
    original_shortfall: float
    new_shortfall: float
    delta_shortfall: float
    impact_summary: str
    new_constraint_report: ConstraintReport
    new_liquidity: LiquiditySummary


class HealthScoreResult(BaseModel):
    total_score: float
    payment_timeliness_score: float       # max 30
    runway_buffer_score: float            # max 25
    gst_compliance_score: float           # max 20
    receivable_collection_score: float    # max 15
    cash_reserve_score: float             # max 10
    contributing_factors: list[str] = Field(default_factory=list)
    improvement_tips: list[str] = Field(default_factory=list)


class Badge(BaseModel):
    id: str
    name: str
    description: str
    icon: str = "🏅"
    unlocked: bool = False
    unlock_condition: str = ""


class GamificationStatus(BaseModel):
    level_name: str
    level_number: int
    score: float
    next_level_threshold: float
    badges: list[Badge] = Field(default_factory=list)
    unlocked_badges: list[str] = Field(default_factory=list)
    motivational_message: str = ""


class ReschedulingEntry(BaseModel):
    obligation_id: str
    counterparty_name: str
    original_due_date: date
    proposed_new_date: date
    amount: float
    reason: str
    draft_message: str
    tone: str


class ReschedulingPlan(BaseModel):
    entries: list[ReschedulingEntry] = Field(default_factory=list)
    total_deferred: float = 0.0
    summary: str = ""


class GSTReminder(BaseModel):
    form_name: str
    description: str
    due_date: date
    days_until_due: int
    is_overdue: bool = False
    penalty_info: str = ""


class EngineOutput(BaseModel):
    liquidity: LiquiditySummary
    constraint_report: ConstraintReport
    explanations: list[ExplanationStep] = Field(default_factory=list)
    health_score: Optional[HealthScoreResult] = None
    gamification: Optional[GamificationStatus] = None
    rescheduling_plan: Optional[ReschedulingPlan] = None
    gst_reminders: list[GSTReminder] = Field(default_factory=list)
