"""
Gamification Layer
──────────────────
Maps health score to levels, evaluates badge conditions,
provides motivational messaging. Pure rule-based logic.
"""

from __future__ import annotations
from schemas import HealthScoreResult, GamificationStatus, Badge

# ── Level Thresholds ─────────────────────────────────────────────────────
LEVELS = [
    (0,  "🌱 Seedling",       1, 25),
    (25, "🌿 Growing",        2, 50),
    (50, "🌳 Stable",         3, 70),
    (70, "💪 Healthy",        4, 85),
    (85, "🏆 Thriving",       5, 100),
]

# ── Badge Definitions ────────────────────────────────────────────────────
BADGE_DEFS = [
    Badge(
        id="first_steps",
        name="First Steps",
        description="Achieved a health score above 20",
        icon="🎯",
        unlock_condition="Health score > 20",
    ),
    Badge(
        id="cash_guardian",
        name="Cash Guardian",
        description="Maintained cash reserve ratio above 50%",
        icon="🛡️",
        unlock_condition="Cash reserve score ≥ 5/10",
    ),
    Badge(
        id="on_time_hero",
        name="On-Time Hero",
        description="Payment timeliness score above 80%",
        icon="⏰",
        unlock_condition="Payment score ≥ 24/30",
    ),
    Badge(
        id="runway_master",
        name="Runway Master",
        description="Maintained 30+ days of cash runway",
        icon="✈️",
        unlock_condition="Runway buffer score = 25/25",
    ),
    Badge(
        id="gst_compliant",
        name="GST Champion",
        description="100% GST filing compliance",
        icon="📋",
        unlock_condition="GST compliance score = 20/20",
    ),
    Badge(
        id="financial_elite",
        name="Financial Elite",
        description="Achieved overall health score above 85",
        icon="👑",
        unlock_condition="Total score > 85",
    ),
]


def _evaluate_badges(score: HealthScoreResult) -> list[Badge]:
    """Evaluate which badges are unlocked based on current score."""
    badges = []
    for b_def in BADGE_DEFS:
        badge = b_def.model_copy()

        if badge.id == "first_steps":
            badge.unlocked = score.total_score > 20
        elif badge.id == "cash_guardian":
            badge.unlocked = score.cash_reserve_score >= 5
        elif badge.id == "on_time_hero":
            badge.unlocked = score.payment_timeliness_score >= 24
        elif badge.id == "runway_master":
            badge.unlocked = score.runway_buffer_score >= 25
        elif badge.id == "gst_compliant":
            badge.unlocked = score.gst_compliance_score >= 20
        elif badge.id == "financial_elite":
            badge.unlocked = score.total_score > 85

        badges.append(badge)
    return badges


def get_gamification_status(score: HealthScoreResult) -> GamificationStatus:
    """Map health score to level + badges + motivational message."""
    # Determine level
    level_name = LEVELS[0][1]
    level_number = 1
    next_threshold = LEVELS[0][3]

    for threshold, name, num, next_t in LEVELS:
        if score.total_score >= threshold:
            level_name = name
            level_number = num
            next_threshold = next_t

    # Evaluate badges
    badges = _evaluate_badges(score)
    unlocked_ids = [b.id for b in badges if b.unlocked]

    # Motivational message based on score
    if score.total_score >= 85:
        msg = "Outstanding! Your financial discipline is exemplary. Keep maintaining this standard!"
    elif score.total_score >= 70:
        msg = "Great progress! You're close to the Thriving tier. Focus on clearing overdue items."
    elif score.total_score >= 50:
        msg = "You're building momentum. Pay attention to runway buffer and payment timeliness."
    elif score.total_score >= 25:
        msg = "Room to grow! Start by paying obligations on time and filing GST returns regularly."
    else:
        msg = "Let's get started! Focus on one area at a time — payment timeliness is a good place to begin."

    return GamificationStatus(
        level_name=level_name,
        level_number=level_number,
        score=score.total_score,
        next_level_threshold=next_threshold,
        badges=badges,
        unlocked_badges=unlocked_ids,
        motivational_message=msg,
    )
