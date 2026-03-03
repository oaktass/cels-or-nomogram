"""
CELS-OC Conversion Score — Digital Nomogram

Run:  streamlit run frontend/app.py
"""

from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from backend.calibration import score_to_probability
from backend.model import PREDICTOR_MAP, RESEARCH_DISCLAIMER, RISK_COLORS
from backend.scoring import compute_score
from frontend.plots import (
    create_component_waterfall,
    create_nomogram_axis,
    create_probability_bar,
    create_risk_band,
    create_score_gauge,
)

st.set_page_config(
    page_title="CELS-OC Conversion Score",
    page_icon="\u2022",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body,
.main, .main .block-container,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div,
div[data-testid="stExpander"],
div[data-testid="stExpander"] > div {
    background-color: #ffffff !important;
    background: #ffffff !important;
    border: none !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] {
    border-right: 1px solid #E5E5E5;
}

.main .block-container {
    max-width: 1200px;
    padding-top: 0.8rem;
}

*:not([class*="icon"]):not([data-testid="stIconMaterial"]):not([class*="material"]):not(i) {
    font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
[data-testid="stIconMaterial"],
[class*="material-icons"],
[class*="icon"] {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
}

h1, h2, h3, h4, h5, h6 { color: #000000 !important; }
p, li, span, label, td, th { color: #000000 !important; }
div:not(.disclaimer-box):not(.sh):not(.rb):not(.co):not(.co-warn):not(.explain-card):not(.hint):not(.algo-box) {
    color: #000000;
}

/* Streamlit dark-theme hardening: force widget and markdown text visible */
[data-testid="stMarkdownContainer"],
[data-testid="stText"],
[data-testid="stCaptionContainer"],
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-baseweb="checkbox"] > label,
[data-baseweb="checkbox"] span {
    color: #000000 !important;
}

hr { border: none !important; border-top: 1px solid #E5E5E5 !important; }

.app-title {
    text-align: center;
    font-size: 1.7rem;
    font-weight: 700;
    color: #000000 !important;
    margin: 0;
    padding: 0;
    line-height: 1.3;
}

.app-subtitle {
    text-align: center;
    font-size: 0.85rem;
    font-weight: 400;
    color: #444444 !important;
    margin: 2px 0 10px 0;
    line-height: 1.5;
}

.disclaimer-box {
    text-align: center;
    font-size: 0.78rem;
    font-weight: 500;
    color: #666666 !important;
    border: 1px solid #E5E5E5;
    padding: 7px 14px;
    margin: 0 auto 12px auto;
    max-width: 680px;
    letter-spacing: 0.2px;
    background: #ffffff !important;
}

.sh {
    font-size: 0.68rem;
    font-weight: 600;
    color: #888888 !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 12px;
    margin-bottom: 3px;
}

.rb {
    display: inline-block;
    padding: 5px 18px;
    font-weight: 600;
    font-size: 0.88rem;
    letter-spacing: 0.4px;
    text-align: center;
    border: 1px solid #E5E5E5;
}
.rb-LOW   { background: #f0fdf4 !important; color: #166534 !important; border-color: #bbf7d0; }
.rb-INTER { background: #fffbeb !important; color: #92400e !important; border-color: #fde68a; }
.rb-HIGH  { background: #fef2f2 !important; color: #991b1b !important; border-color: #fecaca; }

.co {
    border-left: 3px solid #000000;
    padding: 8px 12px;
    font-size: 0.88rem;
    margin: 6px 0;
    background: #ffffff !important;
    color: #000000 !important;
}

.co-warn {
    border-left: 3px solid #d97706;
    padding: 8px 12px;
    font-size: 0.85rem;
    margin: 6px 0;
    background: #ffffff !important;
    color: #000000 !important;
}

.ct { width: 100%; border-collapse: collapse; font-size: 0.84rem; background: #ffffff !important; }
.ct th {
    padding: 6px 8px; text-align: left; font-weight: 600;
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.5px;
    border-bottom: 2px solid #E5E5E5; color: #888888 !important;
    background: #ffffff !important;
}
.ct td {
    padding: 6px 8px; border-bottom: 1px solid #f0f0f0;
    color: #000000 !important; background: #ffffff !important;
}
.ct tr.on td { background: #fafafa !important; }
.ct tr.off td { color: #cccccc !important; }
.ct .note { font-size: 0.72rem; color: #444444 !important; }

.explain-card {
    background: #ffffff !important;
    border: 1px solid #E5E5E5;
    padding: 14px 16px;
    margin-top: 6px;
    line-height: 1.8;
    font-size: 0.88rem;
    color: #000000 !important;
}
.explain-card .ex-label { font-weight: 600; color: #000000 !important; }
.explain-card .ex-pts { font-weight: 600; color: #000000 !important; }
.explain-card .ex-note { font-size: 0.8rem; color: #444444 !important; padding-left: 18px; }
.explain-card .ex-total {
    margin-top: 8px; padding-top: 8px;
    border-top: 1px solid #E5E5E5;
    font-weight: 600; color: #000000 !important;
}

.mp {
    border: 1px solid #E5E5E5;
    padding: 14px;
    font-size: 0.85rem;
    line-height: 1.7;
    color: #000000 !important;
    background: #ffffff !important;
}
.mp strong { color: #000000 !important; }
.mp td, .mp th { color: #000000 !important; }

.algo-box {
    border: 1px solid #E5E5E5;
    padding: 12px 14px;
    font-size: 0.84rem;
    line-height: 1.7;
    color: #000000 !important;
    background: #ffffff !important;
    margin-top: 8px;
}
.algo-box strong { color: #000000 !important; }

.hint {
    font-size: 0.76rem;
    padding-left: 2px;
    margin-top: -4px;
}
.hint-off { color: #aaaaaa !important; }
.hint-on  { color: #444444 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Title + disclaimer
# ---------------------------------------------------------------------------
st.markdown(
    '<h1 class="app-title">CELS-OC Conversion Score</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="app-subtitle">'
    'Digital Nomogram - Intraoperative Decision Support for Completion of '
    'CELS (combined endoscopic-laparoscopic surgery) vs Conversion to '
    'OC (oncologic colectomy)</p>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="disclaimer-box">{RESEARCH_DISCLAIMER}</div>',
    unsafe_allow_html=True,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("#### Clinical Predictors")
    st.caption("Select all findings present intraoperatively.")
    st.markdown("---")

    ulcer_or_depression = st.checkbox(
        "Ulceration or Depression (+3 pts)",
        help=PREDICTOR_MAP["ulcer_or_depression"].description,
    )

    no_lift_sign = st.checkbox(
        "Non-lifting Sign (+3 pts, or +1 with prior intervention)",
        help=PREDICTOR_MAP["no_lift_sign"].description,
    )

    prior_intervention = st.checkbox(
        "Prior Intervention / Scar /Regrowth Tumor (effect modifier)",
        disabled=not no_lift_sign,
        help=PREDICTOR_MAP["prior_intervention"].description,
    )

    if not no_lift_sign:
        st.markdown('<p class="hint hint-off">Enable non-lifting sign to activate this modifier.</p>', unsafe_allow_html=True)
    elif prior_intervention:
        st.markdown('<p class="hint hint-on">Effect modifier active: non-lifting sign weight reduced 3 &rarr; 1 pt.</p>', unsafe_allow_html=True)

    st.markdown("---")

    lesion_size_ge_40 = st.checkbox(
        "Lesion Size \u2265 40 mm (+2 pts)",
        help=PREDICTOR_MAP["lesion_size_ge_40"].description,
    )
    high_grade_dysplasia = st.checkbox(
        "High-Grade Dysplasia (+1 pt)",
        help=PREDICTOR_MAP["high_grade_dysplasia"].description,
    )
    incomplete_removal = st.checkbox(
        "Incomplete Endoscopic Resection (+1 pt)",
        help=PREDICTOR_MAP["incomplete_removal"].description,
    )

if not no_lift_sign:
    prior_intervention = False

# ---------------------------------------------------------------------------
# Compute
# ---------------------------------------------------------------------------
result = compute_score(
    ulcer_or_depression=ulcer_or_depression,
    no_lift_sign=no_lift_sign,
    prior_intervention=prior_intervention,
    lesion_size_ge_40=lesion_size_ge_40,
    high_grade_dysplasia=high_grade_dysplasia,
    incomplete_removal=incomplete_removal,
)
probability = score_to_probability(result.total_score)
pct = probability * 100

RECOMMENDATION_BY_RISK = {
    "LOW": (
        "Complete with CELS<br><br>"
        "&bull; If safe en bloc endoscopic resection achievable &rarr; Finish<br>"
        "&bull; If not endoscopically achievable &rarr; FLEX / CAL-WR (full-thickness)<br>"
        "&bull; Frozen section not required"
    ),
    "INTERMEDIATE": (
        "En Bloc Resection + Frozen Required<br><br>"
        "&bull; If safe en bloc endoscopic resection achievable &rarr; Frozen<br>"
        "&bull; If not endoscopically achievable &rarr; FLEX / CAL-WR + Frozen<br>"
        "&bull; If safe en bloc resection not achievable by any approach &rarr; OC"
    ),
    "HIGH": (
        "Oncologic Priority<br><br>"
        "&bull; If safe en bloc endoscopic resection achievable &rarr; Frozen<br>"
        "&bull; If not endoscopically achievable &rarr; Direct OC<br>"
        "&bull; Do not attempt FLEX / CAL-WR"
    ),
}

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
col_left, col_center, col_right = st.columns([3, 4, 3])

with col_left:
    st.markdown('<div class="sh">Score breakdown</div>', unsafe_allow_html=True)
    st.plotly_chart(
        create_score_gauge(result.total_score, result.max_score, result.risk_category),
        use_container_width=True, config={"displayModeBar": False},
    )

    rows = ""
    for c in result.components:
        cls = "on" if c.active else "off"
        chk = "\u2713" if c.active else "\u2014"
        pts = f"+{c.points}" if c.points > 0 else "0"
        note = f'<br><span class="note">{c.note}</span>' if c.note else ""
        rows += (
            f"<tr class='{cls}'>"
            f"<td style='width:20px;text-align:center;'>{chk}</td>"
            f"<td>{c.label}{note}</td>"
            f"<td style='text-align:center;font-weight:600;'>{pts}</td>"
            f"</tr>"
        )
    st.markdown(
        f'<table class="ct">'
        f"<thead><tr><th></th><th>Predictor</th><th style='text-align:center;'>Pts</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )

with col_center:
    st.markdown('<div class="sh">Nomogram</div>', unsafe_allow_html=True)
    st.plotly_chart(
        create_nomogram_axis(result.total_score, probability, result.risk_category),
        use_container_width=True, config={"displayModeBar": False},
    )
    st.markdown('<div class="sh">Risk zones</div>', unsafe_allow_html=True)
    st.plotly_chart(
        create_risk_band(),
        use_container_width=True, config={"displayModeBar": False},
    )
    st.markdown('<div class="sh">Point contributions</div>', unsafe_allow_html=True)
    cd = [{"label": c.label, "active": c.active, "points": c.points} for c in result.components]
    st.plotly_chart(
        create_component_waterfall(cd),
        use_container_width=True, config={"displayModeBar": False},
    )

with col_right:
    st.markdown('<div class="sh">Predicted probability of OC conversion</div>', unsafe_allow_html=True)

    risk_color = RISK_COLORS[result.risk_category]
    st.markdown(
        f"<h2 style='text-align:center;color:{risk_color} !important;margin:4px 0;'>"
        f"{pct:.1f}%</h2>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        create_probability_bar(probability, result.risk_category),
        use_container_width=True, config={"displayModeBar": False},
    )

    st.markdown('<div class="sh">Risk category</div>', unsafe_allow_html=True)
    badge_cls = {"LOW": "rb-LOW", "INTERMEDIATE": "rb-INTER", "HIGH": "rb-HIGH"}[result.risk_category]
    st.markdown(
        f'<div style="text-align:center;margin:4px 0;">'
        f'<span class="rb {badge_cls}">{result.risk_category}</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sh">Recommendation</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="co">{RECOMMENDATION_BY_RISK[result.risk_category]}</div>', unsafe_allow_html=True)

    if result.interaction_explanation:
        st.markdown('<div class="sh">Interaction effect</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="co-warn">{result.interaction_explanation}</div>', unsafe_allow_html=True)

    # ---- Explainability ----
    st.markdown("---")
    st.markdown('<div class="sh">Explainability</div>', unsafe_allow_html=True)

    active_comps = [c for c in result.components if c.active]
    if active_comps:
        explain_lines = ""
        for c in active_comps:
            if c.points > 0:
                explain_lines += (
                    f'<div>\u2022 <span class="ex-label">{c.label}:</span> '
                    f'<span class="ex-pts">+{c.points} pt{"s" if c.points != 1 else ""}</span></div>'
                )
            else:
                explain_lines += (
                    f'<div>\u2022 <span class="ex-label">{c.label}:</span> '
                    f'<span class="ex-pts">0 pts</span> (modifier)</div>'
                )
            if c.note:
                explain_lines += f'<div class="ex-note">\u2192 {c.note}</div>'

        explain_lines += (
            f'<div class="ex-total">'
            f'Total: {result.total_score} / {result.max_score} '
            f'&rarr; P(OC conversion) = {pct:.1f}%</div>'
        )
        st.markdown(f'<div class="explain-card">{explain_lines}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="explain-card" style="color:#888888 !important;">'
            'No active predictors selected.</div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Risk Stratification Algorithm
# ---------------------------------------------------------------------------
st.markdown("---")

st.markdown(
    '<h3 style="font-size:1.05rem;font-weight:700;color:#000000 !important;margin-bottom:10px;">'
    'Score-Based Decision Algorithm</h3>',
    unsafe_allow_html=True,
)

st.markdown("""
<div class="algo-box">

<strong>LOW RISK (0-3 Points)</strong><br>
Complete with CELS<br><br>
&bull; If safe endoscopic resection achievable<br>
&nbsp;&nbsp;-- Finish<br>
&bull; If not endoscopically achievable<br>
&nbsp;&nbsp;-- FLEX / CAL-WR (full-thickness)<br>
&nbsp;&nbsp;-- Frozen section not required

<br><br>

<strong>INTERMEDIATE RISK (4-6 Points)</strong><br>
En Bloc Resection + Frozen Required<br><br>
&bull; If safe en bloc endoscopic resection achievable<br>
&nbsp;&nbsp;-- Frozen<br>
&bull; If not endoscopically achievable<br>
&nbsp;&nbsp;-- FLEX / CAL-WR + Frozen<br>
&bull; If safe en bloc resection not achievable by any approach<br>
&nbsp;&nbsp;-- OC

<br><br>

<strong>HIGH RISK (7-10 Points)</strong><br>
Oncologic Priority<br><br>
&bull; If safe en bloc endoscopic resection achievable<br>
&nbsp;&nbsp;-- Frozen<br>
&bull; If not endoscopically achievable<br>
&nbsp;&nbsp;-- Direct OC<br>
&bull; Do not attempt FLEX / CAL-WR

</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Method and Model Derivation
# ---------------------------------------------------------------------------
st.markdown("---")

st.markdown(
    '<h3 style="font-size:1.05rem;font-weight:700;color:#000000 !important;margin-bottom:10px;">'
    'Method and Model Derivation</h3>',
    unsafe_allow_html=True,
)

st.markdown("""
<div class="mp">

**Study Design**

Retrospective cohort study of patients undergoing combined endoscopic-laparoscopic
surgery (CELS) for complex colorectal lesions.

**Model Derivation**

A multivariable Firth penalized logistic regression was fit to predict intraoperative
conversion to oncologic colectomy. Firth's method was selected to address small-sample
bias and separation in maximum likelihood estimation.

**Selected Predictors (point-based scoring system)**

| Predictor | Points |
|---|---|
| Ulceration or depression | 3 |
| Non-lifting sign (no prior intervention) | 3 |
| Non-lifting sign (with prior intervention) | 1 |
| Lesion size &ge; 40 mm | 2 |
| High-grade dysplasia | 1 |
| Incomplete endoscopic resection | 1 |

**Effect Modification**

Prior intervention does not contribute points independently. Instead, it modifies
the weight of the non-lifting sign, reducing it from 3 to 1 point. This interaction
reflects the reduced specificity of the non-lifting sign in a previously treated submucosal
plane, where fibrosis from prior intervention may mimic invasive pathology.

**Risk Stratification**

- **LOW RISK (0-3 Points):** Complete with CELS; if safe en bloc endoscopic resection achievable -> Finish; if not endoscopically achievable -> FLEX / CAL-WR (full-thickness); frozen section not required
- **INTERMEDIATE RISK (4-6 Points):** En Bloc Resection + Frozen Required; if safe en bloc endoscopic resection achievable -> Frozen; if not endoscopically achievable -> FLEX / CAL-WR + Frozen; if safe en bloc resection not achievable by any approach -> OC
- **HIGH RISK (7-10 Points):** Oncologic Priority; if safe en bloc endoscopic resection achievable -> Frozen; if not endoscopically achievable -> Direct OC; do not attempt FLEX / CAL-WR

**Maximum Score:** 10

**Definitions**

*Prior Intervention:* Any previous therapeutic colonoscopic resection attempt
(ESD or EMR/snare), or the presence of scar, fibrosis, regrowth, or residual lesion
at the same site. Diagnostic biopsy alone is not considered a prior intervention.

*Endoscopic Resection:* A safe, en bloc excision of the lesion within the submucosal
plane with visibly normal lateral and deep margins, performed with or without adjunctive
laparoscopic mobilization or traction assistance.

**Abbreviations**

- **AO** = appendiceal orifice
- **ICV** = ileocecal valve
- **OC** = oncologic colectomy
- **CELS** = combined endoscopic-laparoscopic surgery
- **FLEX** = Full thickness endolaparoscopic excision
- **CAL-WR** = Colonoscopy assisted laparoscopic Wedge Resection

</div>
""", unsafe_allow_html=True)
