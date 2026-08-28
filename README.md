# Higher Education Return on Investment (ROI) Pipeline

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Econometrics](https://img.shields.io/badge/Econometrics-OLS%20%7C%20HC3-green.svg)](https://www.statsmodels.org/)
[![Machine Learning](https://img.shields.io/badge/ML-K--Means%20Clustering-orange.svg)](https://scikit-learn.org/)

**Author:** Donovan Weekley  
**Institution:** University of Illinois at Urbana-Champaign (BA in Economics, Minor in Data Science)  
**Portfolio:** [github.com/donovanweekley](https://github.com/donovanweekley) | [linkedin.com/in/donovan-weekley](https://linkedin.com/in/donovan-weekley)

---

## Project Overview

This project implements an automated econometric and data pipeline that aggregates multi-source public datasets (U.S. Department of Education College Scorecard, U.S. Census Bureau Table P-24, and ACS Field of Degree) to model post-graduation financial outcomes, capital efficiency, and debt risk across **6,400+ U.S. higher education institutions** and **220,000+ degree programs**.

### Key Questions Answered:
1. **Capital Efficiency & Payback:** How many years does it take for college graduates to break even on tuition and opportunity costs relative to a high school diploma?
2. **The "Major Premium" vs. "College Premium":** Does what you study matter more than where you go?
3. **Debt Risk Elasticity:** How do completion rates, family income aid tiers, and debt-to-earnings ratios impact 20-year Net Present Value (NPV)?

---

## Mathematical & Econometric Methodology

### 1. Capital Efficiency (Debt-Adjusted Net ROI Multiple)

$$
\text{ROI}_{\text{Debt-Adjusted Net}} = \frac{\text{MidCareerPay} - (\text{MedianDebt} + 4 \times \text{AnnualNetCost})}{4 \times \text{AnnualNetCost}}
$$

### 2. Multi-Horizon Net Present Value (NPV)

$$
\text{NPV}(T) = \sum_{t=5}^{T} \frac{\text{Wage}_{\text{College}, t} - \text{Wage}_{\text{HS}, t}}{(1 + r)^t} - \sum_{t=1}^{4} \frac{\text{NetCost}_t + 0.70 \times \text{Wage}_{\text{HS}, t}}{(1 + r)^t}
$$

*Where $r = 0.04$ (4.0% real discount rate), accounting for in-school wage opportunity costs.*

### 3. Estimated Break-Even Payback Period

$$
\text{Payback Period (Years)} = 4 + \frac{4 \times \text{AnnualNetCost} + \text{MedianDebt} + 4 \times 0.50 \times \text{Wage}_{\text{HS}}}{\text{MidCareerPay} - \text{Wage}_{\text{HS}}}
$$

### 4. Econometric Regression (HC3 Robust Standard Errors)

$$
\log(\text{ROI}) = \beta_0 + \beta_1 \log(\text{NetCost}) + \beta_2 \log(\text{Debt}) + \beta_3 \text{CompletionRate} + \beta_4 \text{STEMShare} + \gamma \text{Sector} + \varepsilon
$$

---

## Repository Structure

```text
college-tuition-roi/
├── data/
│   ├── raw/                 # Scorecard zips, Census P-24, ACS tables
│   └── processed/           # High-speed Parquet caches
├── notebooks/
│   ├── higher_ed_roi_pipeline.ipynb  # Primary comprehensive pipeline notebook
│   └── tuition_roi_updated.ipynb     # Legacy prototype & baseline exploratory notebook
├── outputs/
│   ├── figures/             # 300 DPI publication charts
│   └── tables/              # Full CSV summaries & regression logs
├── src/
│   ├── data_loader.py       # Multi-source data extraction & schema normalization
│   ├── roi_calculator.py    # Financial & econometric formulas
│   ├── models.py            # OLS (HC3), Bootstrapping, K-Means clustering
│   ├── visualizations.py    # Publication-ready Seaborn visual generator
│   └── pipeline.py          # Master orchestrator
├── app.py                   # Interactive Streamlit dashboard
├── run_pipeline.py          # One-command CLI pipeline execution
└── requirements.txt         # Project dependencies
```

---

## Quick Start

### 1. Installation
```bash
git clone https://github.com/donovanweekley/College-Tuition-ROI.git
cd College-Tuition-ROI
pip install -r requirements.txt
```

### 2. Run the Full Analytics Pipeline
```bash
python run_pipeline.py
```

### 3. Launch Interactive Streamlit Explorer
```bash
streamlit run app.py
```

---

## Key Findings

| Institutional Sector | Mean Earnings Premium (10-Yr) | 95% Bootstrap CI | Median Payback Period |
| :--- | :--- | :--- | :--- |
| **Public Universities** | +$12,850 / yr | [$11,920, $13,780] | **7.2 years** |
| **Private Non-Profit** | +$18,400 / yr | [$16,900, $19,950] | **11.4 years** |
| **Private For-Profit** | -$14,200 / yr | [-$15,600, -$12,800] | **No Payback** |

*Source: Model estimates using U.S. Dept. of Education College Scorecard and Census P-24 data.*
