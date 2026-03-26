"""
API Contract — Single entry point wrapping all engine modules.
Used for integration testing and potential external consumers.
"""

from __future__ import annotations
from datetime import date
from typing import Optional

from schemas import (
    BusinessState, EngineOutput, WhatIfScenario, WhatIfResult,
    LiquiditySummary, ConstraintReport, HealthScoreResult,
    GamificationStatus, ReschedulingPlan, GSTReminder,
)
from engine.liquidity import get_liquidity_summary
from engine.constraint_detector import detect_constraints
from engine.cot_explainer import explain_decisions
from engine.health_score import compute_health_score
from engine.gamification import get_gamification_status
from engine.rescheduling import generate_rescheduling_plan
from engine.gst_reminders import get_upcoming_gst_deadlines
from engine.scenario_engine import run_what_if


class ThrifteyEngine:
    """Unified API contract for the Thriftey financial engine."""

    def analyze(self, state: BusinessState, payment_history: dict) -> EngineOutput:
        liquidity = get_liquidity_summary(state)
        constraints = detect_constraints(state)
        explanations = explain_decisions(constraints, state)
        health = compute_health_score(state, payment_history)
        gamification = get_gamification_status(health)
        rescheduling = generate_rescheduling_plan(state, constraints)
        gst = get_upcoming_gst_deadlines(state.as_of_date)

        return EngineOutput(
            liquidity=liquidity,
            constraint_report=constraints,
            explanations=explanations,
            health_score=health,
            gamification=gamification,
            rescheduling_plan=rescheduling,
            gst_reminders=gst,
        )

    def what_if(self, state: BusinessState, scenario: WhatIfScenario) -> WhatIfResult:
        return run_what_if(state, scenario)

    def get_liquidity(self, state: BusinessState) -> LiquiditySummary:
        return get_liquidity_summary(state)

    def get_constraints(self, state: BusinessState) -> ConstraintReport:
        return detect_constraints(state)

    def get_health_score(self, state: BusinessState, history: dict) -> HealthScoreResult:
        return compute_health_score(state, history)

    def get_gamification(self, state: BusinessState, history: dict) -> GamificationStatus:
        return get_gamification_status(compute_health_score(state, history))

    def get_rescheduling_plan(self, state: BusinessState) -> ReschedulingPlan:
        return generate_rescheduling_plan(state, detect_constraints(state))

    def get_gst_reminders(self, today: date) -> list[GSTReminder]:
        return get_upcoming_gst_deadlines(today)
