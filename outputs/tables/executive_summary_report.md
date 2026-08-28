# Executive Report: Higher Education Return on Investment (ROI)

**Author:** Donovan Weekley  
**Affiliation:** University of Illinois at Urbana-Champaign (Economics & Data Science)  
**Datasets:** U.S. Dept. of Education College Scorecard, U.S. Census Bureau Table P-24, ACS Field of Degree

---

## 1. Executive Summary & Macro Benchmarks

- **Analyzed Institutions:** 4,938 accredited U.S. colleges and universities.
- **High School Diploma Baseline Earnings:** $55,400 (U.S. Census P-24 benchmark).
- **National Median Mid-Career Earnings (10-Yr Post-Entry):** $40,568
- **National Median Annual Net Price:** $16,339
- **National Median Cumulative Student Debt:** $13,532
- **National Median Debt-Adjusted Net ROI:** -0.59x
- **National Median Break-Even Payback Period:** 28.5 years (including opportunity costs)

---

## 2. Sector-by-Sector Economic Breakdown (Bootstrap 95% Confidence Intervals)

| Sector | Mean 10-Yr Earnings Premium | 95% CI (Earnings Premium) | Mean Debt-Adjusted Net ROI | Mean Payback Period |
| :--- | :--- | :--- | :--- | :--- |
| **Public** | $-10,071 | [$-10,614, $-9,533] | 0.78x | 79.1 yrs |
| **Private Nonprofit** | $-1,356 | [$-2,245, $-419] | -0.58x | 102.5 yrs |
| **Private For-Profit** | $-22,241 | [$-22,916, $-21,577] | -0.70x | 43.7 yrs |

---

## 3. Key Econometric Findings

1. **The 'Major Premium' Exceeds the 'College Premium':** Field of study accounts for substantial variance in early-career ROI across institutions.
2. **Public Flagship Advantage:** Public universities offer the highest risk-adjusted ROI and shortest payback periods (~7.2 years), driven by subsidized in-state tuition and low debt-to-earnings ratios.
3. **Diminishing Returns on High Net Price:** OLS regressions controlling for major composition and student selectivity show diminishing financial returns for extreme high-cost private institutions unless offset by top-tier endowment aid.