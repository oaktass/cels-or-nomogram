"""
CELS-OR Prediction Score — Probability Calibration

Monotonic logistic mapping from integer score (0–10) to predicted
probability of OR conversion.

Parameters were estimated by fitting a logistic regression of the
OR outcome on the integer CELS score in the derivation cohort (n=70).

    P(OR conversion | score) = 1 / (1 + exp(-(α + β × score)))

    α (intercept)  = -3.8132
    β (coefficient) =  0.7584

Model discrimination: derived from Firth penalized logistic regression.
Calibration verified against observed conversion rates per score stratum.
"""

from __future__ import annotations

import math

CALIBRATION_INTERCEPT: float = -3.8132
CALIBRATION_SLOPE: float = 0.7584


def score_to_probability(score: int) -> float:
    """Map an integer CELS score to a calibrated probability of OR conversion."""
    if not 0 <= score <= 10:
        raise ValueError(f"Score must be 0–10, got {score}")
    logit = CALIBRATION_INTERCEPT + CALIBRATION_SLOPE * score
    return 1.0 / (1.0 + math.exp(-logit))


def get_probability_table() -> dict[int, float]:
    """Return a lookup table of score → probability for all valid scores."""
    return {s: score_to_probability(s) for s in range(11)}


PROBABILITY_TABLE: dict[int, float] = get_probability_table()
