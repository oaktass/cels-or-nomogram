"""
OC Conversion Score — Scoring Engine

Deterministic point-based scoring with effect modification logic.

Interaction rule:
    Prior intervention does NOT contribute points independently.
    Instead, it attenuates the weight of the no-lift sign:
        - No-lift sign WITHOUT prior intervention -> 3 points
        - No-lift sign WITH prior intervention    -> 1 point

    If no_lift_sign is False, prior_intervention has no scoring effect.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import (
    MAX_SCORE,
    NO_LIFT_POINTS_WITH_PRIOR,
    NO_LIFT_POINTS_WITHOUT_PRIOR,
    PREDICTOR_MAP,
    RISK_RECOMMENDATIONS,
    RISK_THRESHOLDS,
)


@dataclass
class ScoreComponent:
    predictor_key: str
    label: str
    active: bool
    points: int
    note: str = ""


@dataclass
class ScoreResult:
    total_score: int
    max_score: int
    components: list[ScoreComponent]
    risk_category: str
    recommendation: str
    interaction_active: bool
    interaction_explanation: str


def compute_score(
    ulcer_or_depression: bool = False,
    no_lift_sign: bool = False,
    prior_intervention: bool = False,
    lesion_size_ge_40: bool = False,
    high_grade_dysplasia: bool = False,
    incomplete_removal: bool = False,
) -> ScoreResult:
    """Compute the OC conversion score from binary predictor inputs."""
    components: list[ScoreComponent] = []
    total = 0

    # --- Ulceration / depression / Paris 2c-3 -> 3 pts ---
    pts = 3 if ulcer_or_depression else 0
    components.append(ScoreComponent(
        predictor_key="ulcer_or_depression",
        label=PREDICTOR_MAP["ulcer_or_depression"].label,
        active=ulcer_or_depression,
        points=pts,
    ))
    total += pts

    # --- No-lift sign with interaction modifier ---
    interaction_active = no_lift_sign and prior_intervention
    if no_lift_sign:
        nls_pts = NO_LIFT_POINTS_WITH_PRIOR if prior_intervention else NO_LIFT_POINTS_WITHOUT_PRIOR
    else:
        nls_pts = 0

    nls_note = ""
    if interaction_active:
        nls_note = (
            "Prior intervention attenuates no-lift sign weight "
            f"(3 \u2192 {NO_LIFT_POINTS_WITH_PRIOR} pt)"
        )

    components.append(ScoreComponent(
        predictor_key="no_lift_sign",
        label=PREDICTOR_MAP["no_lift_sign"].label,
        active=no_lift_sign,
        points=nls_pts,
        note=nls_note,
    ))
    total += nls_pts

    # Prior intervention: modifier only, zero independent points
    prior_note = ""
    if prior_intervention:
        if no_lift_sign:
            prior_note = "Effect modifier - attenuates no-lift sign from 3 to 1 pt"
        else:
            prior_note = "No scoring effect - no-lift sign is absent"
    components.append(ScoreComponent(
        predictor_key="prior_intervention",
        label=PREDICTOR_MAP["prior_intervention"].label,
        active=prior_intervention,
        points=0,
        note=prior_note,
    ))

    # --- Lesion size >= 40 mm -> 2 pts ---
    pts = 2 if lesion_size_ge_40 else 0
    components.append(ScoreComponent(
        predictor_key="lesion_size_ge_40",
        label=PREDICTOR_MAP["lesion_size_ge_40"].label,
        active=lesion_size_ge_40,
        points=pts,
    ))
    total += pts

    # --- High-grade dysplasia -> 1 pt ---
    pts = 1 if high_grade_dysplasia else 0
    components.append(ScoreComponent(
        predictor_key="high_grade_dysplasia",
        label=PREDICTOR_MAP["high_grade_dysplasia"].label,
        active=high_grade_dysplasia,
        points=pts,
    ))
    total += pts

    # --- Incomplete endoluminal resection -> 1 pt ---
    pts = 1 if incomplete_removal else 0
    components.append(ScoreComponent(
        predictor_key="incomplete_removal",
        label=PREDICTOR_MAP["incomplete_removal"].label,
        active=incomplete_removal,
        points=pts,
    ))
    total += pts

    # --- Risk stratification ---
    risk_category = _classify_risk(total)
    recommendation = RISK_RECOMMENDATIONS[risk_category]

    interaction_explanation = ""
    if interaction_active:
        interaction_explanation = (
            "Effect modification: Prior intervention attenuates "
            "the predictive weight of the no-lift sign from 3 to 1 point. "
            "This reflects reduced specificity of the no-lift sign in a previously "
            "treated submucosal plane, where fibrosis from prior intervention "
            "may mimic invasive pathology."
        )

    return ScoreResult(
        total_score=total,
        max_score=MAX_SCORE,
        components=components,
        risk_category=risk_category,
        recommendation=recommendation,
        interaction_active=interaction_active,
        interaction_explanation=interaction_explanation,
    )


def _classify_risk(score: int) -> str:
    for category, (lo, hi) in RISK_THRESHOLDS.items():
        if lo <= score <= hi:
            return category
    return "HIGH"
