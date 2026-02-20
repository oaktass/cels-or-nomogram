"""
CELS-OR Prediction Score — FastAPI Backend

Provides a RESTful prediction endpoint for the CELS-OR scoring system.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .calibration import PROBABILITY_TABLE, score_to_probability
from .model import (
    APP_VERSION,
    MODEL_VERSION,
    PREDICTORS,
    RESEARCH_DISCLAIMER,
    RISK_COLORS,
)
from .scoring import compute_score

app = FastAPI(
    title="CELS-OR Prediction Score API",
    description=(
        "Intraoperative decision support for completion of CELS vs "
        "conversion to oncologic resection. " + RESEARCH_DISCLAIMER
    ),
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    ulcer_or_depression: bool = False
    no_lift_sign: bool = False
    prior_resection: bool = False
    lesion_size_ge_40: bool = False
    high_grade_dysplasia: bool = False
    incomplete_removal: bool = False


class ComponentResponse(BaseModel):
    predictor_key: str
    label: str
    active: bool
    points: int
    note: str


class PredictionResponse(BaseModel):
    total_score: int
    max_score: int
    predicted_probability: float
    risk_category: str
    risk_color: str
    recommendation: str
    components: list[ComponentResponse]
    interaction_active: bool
    interaction_explanation: str
    disclaimer: str


@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest) -> PredictionResponse:
    result = compute_score(
        ulcer_or_depression=req.ulcer_or_depression,
        no_lift_sign=req.no_lift_sign,
        prior_resection=req.prior_resection,
        lesion_size_ge_40=req.lesion_size_ge_40,
        high_grade_dysplasia=req.high_grade_dysplasia,
        incomplete_removal=req.incomplete_removal,
    )
    probability = score_to_probability(result.total_score)

    return PredictionResponse(
        total_score=result.total_score,
        max_score=result.max_score,
        predicted_probability=round(probability, 4),
        risk_category=result.risk_category,
        risk_color=RISK_COLORS[result.risk_category],
        recommendation=result.recommendation,
        components=[
            ComponentResponse(
                predictor_key=c.predictor_key,
                label=c.label,
                active=c.active,
                points=c.points,
                note=c.note,
            )
            for c in result.components
        ],
        interaction_active=result.interaction_active,
        interaction_explanation=result.interaction_explanation,
        disclaimer=RESEARCH_DISCLAIMER,
    )


class PredictorInfo(BaseModel):
    key: str
    label: str
    description: str
    base_points: int
    is_interaction_target: bool
    is_interaction_modifier: bool


@app.get("/predictors", response_model=list[PredictorInfo])
def get_predictors() -> list[PredictorInfo]:
    return [
        PredictorInfo(
            key=p.key,
            label=p.label,
            description=p.description,
            base_points=p.base_points,
            is_interaction_target=p.is_interaction_target,
            is_interaction_modifier=p.is_interaction_modifier,
        )
        for p in PREDICTORS
    ]


@app.get("/probability_table")
def get_probability_table() -> dict[str, float]:
    return {str(k): v for k, v in PROBABILITY_TABLE.items()}


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "app_version": APP_VERSION,
        "model_version": MODEL_VERSION,
        "disclaimer": RESEARCH_DISCLAIMER,
    }
