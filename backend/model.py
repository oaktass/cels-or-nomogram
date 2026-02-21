"""
CELS-OR Prediction Score — Model Configuration

Defines predictor metadata, point allocations, and interaction logic
for the Firth penalized logistic regression-derived scoring system.

Reference: [Manuscript under review, Surgical Endoscopy]
"""

from dataclasses import dataclass

APP_VERSION = "1.0.0"
MODEL_VERSION = "1.0.0"

RESEARCH_DISCLAIMER = (
    "FOR RESEARCH PURPOSES ONLY - NOT FOR CLINICAL DECISION MAKING"
)


@dataclass(frozen=True)
class Predictor:
    key: str
    label: str
    description: str
    base_points: int
    is_interaction_target: bool = False
    is_interaction_modifier: bool = False


PREDICTORS: list[Predictor] = [
    Predictor(
        key="ulcer_or_depression",
        label="Ulceration or Depression / Paris 2c-3",
        description="Mucosal ulceration or depression observed on endoscopic evaluation (Paris classification 2c or 3)",
        base_points=3,
    ),
    Predictor(
        key="no_lift_sign",
        label="No-lift Sign",
        description="Failure of submucosal lift after saline injection",
        base_points=3,
        is_interaction_target=True,
    ),
    Predictor(
        key="prior_intervention",
        label="Prior Intervention / Visible Scar / Regrowth Tumor",
        description=(
            "Prior intervention is defined as any previous therapeutic colonoscopic "
            "resection attempt (ESD or EMR/snare), or the presence of scar, fibrosis, "
            "regrowth, or residual lesion at the same site. Diagnostic biopsy alone is "
            "not considered a prior intervention. Effect modifier for no-lift sign."
        ),
        base_points=0,
        is_interaction_modifier=True,
    ),
    Predictor(
        key="lesion_size_ge_40",
        label="Lesion Size \u2265 40 mm",
        description="Greatest dimension of the lesion is 40 mm or larger",
        base_points=2,
    ),
    Predictor(
        key="high_grade_dysplasia",
        label="High-Grade Dysplasia",
        description="Histopathologic finding of high-grade dysplasia on biopsy",
        base_points=1,
    ),
    Predictor(
        key="incomplete_removal",
        label="Incomplete Endoluminal Resection",
        description=(
            "Endoluminal resection is defined as a safe, en bloc excision of the lesion "
            "within the submucosal plane with visibly normal lateral and deep margins, "
            "performed with or without adjunctive laparoscopic mobilization or traction "
            "assistance. This predictor is positive when such resection is judged "
            "macroscopically incomplete."
        ),
        base_points=1,
    ),
]

PREDICTOR_MAP: dict[str, Predictor] = {p.key: p for p in PREDICTORS}

MAX_SCORE = 10

NO_LIFT_POINTS_WITHOUT_PRIOR = 3
NO_LIFT_POINTS_WITH_PRIOR = 1

RISK_THRESHOLDS = {
    "LOW": (0, 3),
    "INTERMEDIATE": (4, 6),
    "HIGH": (7, 10),
}

RISK_RECOMMENDATIONS = {
    "LOW": "Consider completing CELS",
    "INTERMEDIATE": "Individualized decision - consider frozen section analysis",
    "HIGH": "Favor conversion to oncologic resection",
}

RISK_COLORS = {
    "LOW": "#2ecc71",
    "INTERMEDIATE": "#f39c12",
    "HIGH": "#e74c3c",
}
