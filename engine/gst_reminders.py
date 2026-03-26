"""
GST Reminder Engine
───────────────────
Generates upcoming GST filing deadlines based on India's standard
GST calendar. Supports regular taxpayers (GSTR-1, GSTR-3B) and
composition scheme (CMP-08).

Deadlines follow standard rules:
    GSTR-1:  11th of following month
    GSTR-3B: 20th of following month
    CMP-08:  18th of month following quarter end (Apr/Jul/Oct/Jan)

Penalty: ₹50/day (₹25 CGST + ₹25 SGST) for late monthly filing
         ₹200/day for annual returns

No LLM. Pure calendar arithmetic.
"""

from __future__ import annotations
from datetime import date, timedelta
from typing import List

from schemas import GSTReminder


# ── Standard GST Calendar ────────────────────────────────────────────────
MONTHLY_FORMS = [
    {
        "form": "GSTR-1",
        "description": "Outward supply details — monthly sales return",
        "day": 11,
        "penalty": "₹50/day (₹25 CGST + ₹25 SGST). Max ₹5,000 per return.",
    },
    {
        "form": "GSTR-3B",
        "description": "Summary return with tax payment — monthly self-assessment",
        "day": 20,
        "penalty": "₹50/day (₹25 CGST + ₹25 SGST). 18% interest on unpaid tax.",
    },
]

QUARTERLY_FORMS = [
    {
        "form": "CMP-08",
        "description": "Composition scheme quarterly statement",
        "day": 18,
        "months": [4, 7, 10, 1],  # Quarter-end following months
        "penalty": "₹50/day. Must also file GSTR-4 annually.",
    },
]


def _next_occurrence(reference_day: int, today: date) -> date:
    """Find the next occurrence of a specific day of the month."""
    try:
        this_month = date(today.year, today.month, reference_day)
    except ValueError:
        # Handle months with fewer days
        next_m = today.replace(day=28) + timedelta(days=4)
        last = next_m - timedelta(days=next_m.day)
        this_month = date(today.year, today.month, min(reference_day, last.day))

    if this_month >= today:
        return this_month

    # Rollover to next month
    month = today.month + 1
    year = today.year
    if month > 12:
        month = 1
        year += 1
    try:
        return date(year, month, reference_day)
    except ValueError:
        next_m = date(year, month, 28) + timedelta(days=4)
        last = next_m - timedelta(days=next_m.day)
        return date(year, month, min(reference_day, last.day))


def get_upcoming_gst_deadlines(
    today: date,
    lookahead_days: int = 30,
    is_composition_scheme: bool = False,
) -> List[GSTReminder]:
    """Return GST deadlines within the lookahead window."""
    cutoff = today + timedelta(days=lookahead_days)
    reminders: List[GSTReminder] = []

    if not is_composition_scheme:
        for form_def in MONTHLY_FORMS:
            deadline = _next_occurrence(form_def["day"], today)
            if deadline <= cutoff:
                days_until = (deadline - today).days
                is_overdue = days_until < 0

                reminders.append(GSTReminder(
                    form_name=form_def["form"],
                    description=form_def["description"],
                    due_date=deadline,
                    days_until_due=max(0, days_until),
                    is_overdue=is_overdue,
                    penalty_info=form_def["penalty"],
                ))

            # Also check if there's a second occurrence within lookahead
            month = deadline.month + 1
            year = deadline.year
            if month > 12:
                month = 1
                year += 1
            try:
                next_deadline = date(year, month, form_def["day"])
            except ValueError:
                next_m = date(year, month, 28) + timedelta(days=4)
                last = next_m - timedelta(days=next_m.day)
                next_deadline = date(year, month, min(form_def["day"], last.day))

            if next_deadline <= cutoff:
                days_until = (next_deadline - today).days
                reminders.append(GSTReminder(
                    form_name=form_def["form"],
                    description=form_def["description"],
                    due_date=next_deadline,
                    days_until_due=max(0, days_until),
                    is_overdue=False,
                    penalty_info=form_def["penalty"],
                ))
    else:
        for form_def in QUARTERLY_FORMS:
            for target_month in form_def["months"]:
                year = today.year
                if target_month < today.month:
                    year += 1
                try:
                    deadline = date(year, target_month, form_def["day"])
                except ValueError:
                    continue
                if today <= deadline <= cutoff:
                    days_until = (deadline - today).days
                    reminders.append(GSTReminder(
                        form_name=form_def["form"],
                        description=form_def["description"],
                        due_date=deadline,
                        days_until_due=days_until,
                        is_overdue=False,
                        penalty_info=form_def["penalty"],
                    ))

    reminders.sort(key=lambda r: r.due_date)
    return reminders
