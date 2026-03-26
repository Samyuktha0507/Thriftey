"""
Rescheduling Planner & Email Drafting
─────────────────────────────────────
For obligations classified as partial/cannot_pay, generates:
    1. Proposed new dates (7-14 day extensions based on flexibility)
    2. Tone-adapted negotiation email drafts (professional/friendly/formal)

Tone selection is deterministic based on counterparty relationship profile.
Email templates are rule-based — NO LLM.
"""

from __future__ import annotations
from datetime import timedelta
from typing import Optional

from schemas import (
    BusinessState, ConstraintReport, ReschedulingPlan, ReschedulingEntry,
    Flexibility, RelationshipType, ScoredObligation,
)


# ── Extension Days by Flexibility ────────────────────────────────────────
EXTENSION_DAYS = {
    Flexibility.NONE: 0,
    Flexibility.LOW: 5,
    Flexibility.MEDIUM: 10,
    Flexibility.HIGH: 14,
}

# ── Tone by Relationship ─────────────────────────────────────────────────
TONE_MAP = {
    RelationshipType.GOVERNMENT: "formal",
    RelationshipType.LENDER: "formal",
    RelationshipType.EMPLOYEE: "friendly",
    RelationshipType.CRITICAL_SUPPLIER: "professional",
    RelationshipType.REGULAR_SUPPLIER: "professional",
    RelationshipType.UTILITY_PROVIDER: "professional",
    RelationshipType.LANDLORD: "professional",
    RelationshipType.OTHER: "professional",
}


def _draft_message(
    counterparty_name: str,
    amount: float,
    original_date,
    new_date,
    tone: str,
    business_name: str = "Our Business",
) -> str:
    """Generate a tone-adapted email draft. Rule-based templates."""

    if tone == "formal":
        return (
            f"Subject: Request for Payment Extension — ₹{amount:,.0f}\n\n"
            f"Dear {counterparty_name},\n\n"
            f"We respectfully request an extension on our payment obligation of ₹{amount:,.0f}, "
            f"originally due on {original_date}.\n\n"
            f"Due to a temporary cash flow constraint, we propose a revised payment date of {new_date}. "
            f"We remain fully committed to fulfilling this obligation and appreciate your understanding.\n\n"
            f"Please confirm whether this revised timeline is acceptable.\n\n"
            f"Regards,\n{business_name}"
        )
    elif tone == "friendly":
        return (
            f"Subject: Quick Update on Payment — ₹{amount:,.0f}\n\n"
            f"Hi {counterparty_name},\n\n"
            f"Hope you're doing well! I wanted to let you know about a small delay "
            f"in processing the payment of ₹{amount:,.0f} that was due on {original_date}.\n\n"
            f"We're expecting the payment to come through by {new_date}. "
            f"Really appreciate your patience — we value our working relationship!\n\n"
            f"Thanks,\n{business_name}"
        )
    else:  # professional
        return (
            f"Subject: Payment Schedule Update — ₹{amount:,.0f}\n\n"
            f"Dear {counterparty_name},\n\n"
            f"This is to inform you that we need to adjust the payment schedule "
            f"for the ₹{amount:,.0f} obligation originally due on {original_date}.\n\n"
            f"After reviewing our cash flow position, we propose {new_date} as the revised payment date. "
            f"We have taken steps to ensure timely payment by this date.\n\n"
            f"We appreciate your cooperation and look forward to continuing our business relationship.\n\n"
            f"Best regards,\n{business_name}"
        )


def generate_rescheduling_plan(
    state: BusinessState,
    constraint_report: ConstraintReport,
) -> ReschedulingPlan:
    """Generate a rescheduling plan for obligations that can't be paid on time."""

    if not constraint_report.is_constrained:
        return ReschedulingPlan(summary="All obligations can be paid on time. No rescheduling needed.")

    entries = []
    total_deferred = 0.0

    # Build counterparty lookup
    cp_map = {cp.id: cp for cp in state.counterparties}

    for scored in constraint_report.scored_obligations:
        if scored.can_pay in ("partial", "cannot_pay"):
            ob = scored.obligation

            # Look up counterparty
            cp = cp_map.get(ob.counterparty_id)

            # Determine tone
            if cp:
                tone = TONE_MAP.get(cp.relationship, "professional")
            else:
                tone = "professional"

            # Determine extension
            ext_days = EXTENSION_DAYS.get(ob.flexibility, 7)
            if ext_days == 0:
                # Non-flexible obligations (tax, EMI) — cannot reschedule
                continue

            new_date = ob.due_date + timedelta(days=ext_days)

            # Generate draft
            draft = _draft_message(
                counterparty_name=ob.counterparty_name,
                amount=ob.amount,
                original_date=ob.due_date,
                new_date=new_date,
                tone=tone,
                business_name=state.business_name,
            )

            reason = (
                f"Cash shortfall of ₹{constraint_report.shortfall:,.0f} prevents on-time payment. "
                f"This obligation ranked #{scored.rank} with priority score {scored.priority_score:.2f}."
            )

            entries.append(ReschedulingEntry(
                obligation_id=ob.id,
                counterparty_name=ob.counterparty_name,
                original_due_date=ob.due_date,
                proposed_new_date=new_date,
                amount=ob.amount,
                reason=reason,
                draft_message=draft,
                tone=tone,
            ))
            total_deferred += ob.amount

    summary = (
        f"Rescheduling plan: {len(entries)} obligation(s) totalling ₹{total_deferred:,.0f} "
        f"need deferral due to a cash shortfall of ₹{constraint_report.shortfall:,.0f}."
    )

    return ReschedulingPlan(
        entries=entries,
        total_deferred=total_deferred,
        summary=summary,
    )
