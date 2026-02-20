# CELS-OR Prediction Score - Digital Nomogram

> **FOR RESEARCH PURPOSES ONLY - NOT FOR CLINICAL DECISION MAKING**

Interactive digital nomogram for the **CELS-OR Prediction Score**, an intraoperative
decision support tool for completion of Combined Endoscopic-Laparoscopic Surgery (CELS)
versus conversion to oncologic resection.

## Overview

This application implements a point-based scoring system derived from a multivariable
Firth penalized logistic regression model. It provides:

- **Score computation** with automatic interaction-effect handling
- **Calibrated probability** of OR conversion
- **Risk stratification** (Low / Intermediate / High)
- **Graphical nomogram** visualization
- **Interpretable explanation** panel

## Scoring System

| Predictor | Points |
|---|---|
| Ulceration or depression | 3 |
| No-lift sign (no prior resection) | 3 |
| No-lift sign (with prior resection) | 1 |
| Lesion size >= 40 mm | 2 |
| High-grade dysplasia | 1 |
| Incomplete endoscopic removal | 1 |
| **Maximum** | **10** |

### Effect Modification Rule

Previous endoscopic resection does **not** contribute points independently. Instead, it
modifies the weight of the no-lift sign from 3 points to 1 point. This reflects the
reduced specificity of the no-lift sign in a previously resected submucosal plane.

### Risk Stratification

| Score Range | Risk Category | Recommendation |
|---|---|---|
| 0-3 | Low | Consider completing CELS |
| 4-6 | Intermediate | Individualized decision - consider frozen section |
| 7-10 | High | Favor conversion to oncologic resection |

## Disclaimer

This tool is derived from a peer-reviewed research study and is provided
**for research purposes only**. It has not been validated for prospective
clinical use. All clinical decisions must be made by qualified physicians
independent of this tool.
