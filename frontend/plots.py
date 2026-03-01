"""
OC Conversion Score — Visualization Utilities

Minimal clinical visualizations using Plotly.
Pure white backgrounds, black text, light grey borders.
"""

from __future__ import annotations

import plotly.graph_objects as go

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.calibration import PROBABILITY_TABLE
from backend.model import RISK_COLORS

FONT = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
BLACK = "#000000"
GREY = "#666666"
BORDER = "#e0e0e0"
WHITE = "#ffffff"


def create_score_gauge(total_score: int, max_score: int, risk_category: str) -> go.Figure:
    color = RISK_COLORS[risk_category]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total_score,
        number={"font": {"size": 44, "color": BLACK, "family": FONT}},
        title={"text": "OC Conversion Score", "font": {"size": 13, "color": GREY, "family": FONT}},
        gauge={
            "axis": {
                "range": [0, max_score],
                "tickvals": list(range(max_score + 1)),
                "ticktext": [str(i) for i in range(max_score + 1)],
                "tickfont": {"size": 10, "color": GREY, "family": FONT},
                "dtick": 1,
            },
            "bar": {"color": color, "thickness": 0.2},
            "bgcolor": "#f5f5f5",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 3], "color": "rgba(46,204,113,0.06)"},
                {"range": [3, 6], "color": "rgba(243,156,18,0.06)"},
                {"range": [6, 10], "color": "rgba(231,76,60,0.06)"},
            ],
            "threshold": {
                "line": {"color": BLACK, "width": 2},
                "thickness": 0.7,
                "value": total_score,
            },
        },
    ))
    fig.update_layout(
        height=230,
        margin=dict(t=45, b=5, l=20, r=20),
        paper_bgcolor=WHITE,
        font={"family": FONT},
    )
    return fig


def create_probability_bar(probability: float, risk_category: str) -> go.Figure:
    color = RISK_COLORS[risk_category]
    pct = probability * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[pct], y=[""], orientation="h",
        marker=dict(color=color, line=dict(width=0)),
        text=f"{pct:.1f}%",
        textposition="inside",
        textfont=dict(size=14, color="white", family=FONT),
        hoverinfo="none",
    ))
    fig.add_trace(go.Bar(
        x=[100 - pct], y=[""], orientation="h",
        marker=dict(color="#f0f0f0"),
        hoverinfo="none", showlegend=False,
    ))
    fig.update_layout(
        barmode="stack", height=44,
        margin=dict(t=0, b=0, l=0, r=0),
        xaxis=dict(range=[0, 100], showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        showlegend=False,
    )
    return fig


def create_risk_band() -> go.Figure:
    fig = go.Figure()
    bands = [
        ("LOW (0\u20133)", 0, 3.5, RISK_COLORS["LOW"]),
        ("INTERMEDIATE (4\u20136)", 3.5, 6.5, RISK_COLORS["INTERMEDIATE"]),
        ("HIGH (7\u201310)", 6.5, 10, RISK_COLORS["HIGH"]),
    ]
    for label, x0, x1, color in bands:
        fig.add_shape(
            type="rect", x0=x0, x1=x1, y0=0, y1=1,
            fillcolor=color, opacity=0.7, line_width=0,
        )
        fig.add_annotation(
            x=(x0 + x1) / 2, y=0.5, text=label, showarrow=False,
            font=dict(size=10, color="white", family=FONT),
        )
    fig.update_layout(
        height=42, margin=dict(t=0, b=0, l=0, r=0),
        xaxis=dict(range=[0, 10], showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(range=[0, 1], showticklabels=False, showgrid=False, zeroline=False),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
    )
    return fig


def create_nomogram_axis(total_score: int, probability: float, risk_category: str) -> go.Figure:
    color = RISK_COLORS[risk_category]
    probs = PROBABILITY_TABLE
    scores = sorted(probs.keys())

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=scores, y=[probs[s] * 100 for s in scores],
        mode="lines+markers",
        line=dict(color=BLACK, width=1.5),
        marker=dict(size=4, color=BLACK),
        name="Predicted probability",
        hovertemplate="Score %{x}<br>P(OC) = %{y:.1f}%<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=[total_score], y=[probability * 100],
        mode="markers+text",
        marker=dict(size=12, color=color, symbol="diamond", line=dict(color=BLACK, width=1)),
        text=[f"{probability * 100:.1f}%"],
        textposition="top center",
        textfont=dict(size=11, color=BLACK, family=FONT),
        name="Current patient",
        hoverinfo="skip",
    ))

    fig.add_vrect(x0=-0.3, x1=3.5, fillcolor=RISK_COLORS["LOW"], opacity=0.04, line_width=0)
    fig.add_vrect(x0=3.5, x1=6.5, fillcolor=RISK_COLORS["INTERMEDIATE"], opacity=0.04, line_width=0)
    fig.add_vrect(x0=6.5, x1=10.3, fillcolor=RISK_COLORS["HIGH"], opacity=0.04, line_width=0)

    for b in [3.5, 6.5]:
        fig.add_vline(x=b, line=dict(color=BORDER, width=1, dash="dash"))

    fig.update_layout(
        height=300, margin=dict(t=25, b=45, l=50, r=15),
        xaxis=dict(
            title=dict(text="OC Conversion Score", font=dict(size=11, color=GREY)),
            range=[-0.3, 10.3], tickvals=list(range(11)), dtick=1,
            gridcolor=BORDER, tickfont=dict(color=GREY, size=10),
        ),
        yaxis=dict(
            title=dict(text="P(OC Conversion) %", font=dict(size=11, color=GREY)),
            range=[-2, 105], tickvals=[0, 20, 40, 60, 80, 100],
            gridcolor=BORDER, tickfont=dict(color=GREY, size=10),
        ),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        font=dict(family=FONT, color=BLACK),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
            font=dict(size=9, color=GREY),
        ),
    )
    return fig


def create_component_waterfall(components: list[dict]) -> go.Figure:
    active = [c for c in components if c["active"] and c["points"] > 0]
    if not active:
        fig = go.Figure()
        fig.add_annotation(
            text="No active predictors", xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=12, color=GREY, family=FONT),
        )
        fig.update_layout(
            height=160, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor=WHITE, plot_bgcolor=WHITE,
            xaxis=dict(visible=False), yaxis=dict(visible=False),
        )
        return fig

    labels = [c["label"] for c in active] + ["Total"]
    values = [c["points"] for c in active]
    total_val = sum(values)
    measures = ["relative"] * len(values) + ["total"]
    values.append(total_val)

    fig = go.Figure(go.Waterfall(
        x=labels, y=values, measure=measures,
        connector={"line": {"color": BORDER}},
        increasing={"marker": {"color": "#555555"}},
        totals={"marker": {"color": BLACK}},
        textposition="outside",
        text=[f"+{v}" if m == "relative" else str(v) for v, m in zip(values, measures)],
        textfont=dict(size=11, family=FONT, color=BLACK),
    ))
    fig.update_layout(
        height=230, margin=dict(t=15, b=65, l=40, r=15),
        yaxis=dict(title="Points", gridcolor=BORDER, tickfont=dict(color=GREY, size=10)),
        xaxis=dict(tickangle=-25, tickfont=dict(color=GREY, size=9)),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        font=dict(family=FONT, color=BLACK),
        showlegend=False,
    )
    return fig
