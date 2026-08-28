"""
Financial and Econometric ROI Modeling Module
Computes:
  - Debt-Adjusted Net ROI (Capital Efficiency Ratio)
  - Earnings Premium relative to Census High School Baseline
  - Debt Burden Metrics (Debt-to-Earnings, Monthly Debt Service)
  - Discounted Cash Flow Net Present Value (10-year, 20-year, 30-year NPV)
  - Internal Rate of Return (IRR)
  - Break-Even Payback Period (incorporating Opportunity Cost)
  - Major-Level (Field of Study) Return Benchmarks
"""

import numpy as np
import pandas as pd
from scipy.optimize import brentq


def calculate_monthly_debt_payment(principal: float, annual_interest_rate: float = 0.055, term_years: int = 10) -> float:
    """
    Calculates monthly payment on a standard fixed-rate amortized loan.
    Formula: P * (r*(1+r)^n) / ((1+r)^n - 1)
    """
    if pd.isna(principal) or principal <= 0:
        return 0.0
    r = annual_interest_rate / 12.0
    n = term_years * 12
    return principal * (r * (1 + r)**n) / ((1 + r)**n - 1)


def calculate_npv(annual_net_cost: float, college_earnings: float, hs_baseline: float,
                  horizon_years: int = 20, discount_rate: float = 0.04,
                  degree_duration: int = 4, wage_growth_rate: float = 0.02) -> float:
    """
    Calculates Net Present Value (NPV) of a college degree over a specified horizon.
    Accounts for 4 years of net tuition payments + opportunity cost (foregone HS wages),
    followed by post-graduation earnings premiums with real wage growth.
    """
    if pd.isna(annual_net_cost) or pd.isna(college_earnings) or pd.isna(hs_baseline):
        return np.nan

    cash_flows = []
    # Years 1 to degree_duration: In School (Tuition + partial opportunity cost)
    # Assuming student works part-time (foregoing 70% of full-time HS earnings)
    in_school_opp_cost = 0.70 * hs_baseline
    annual_investment = -(annual_net_cost + in_school_opp_cost)
    
    for t in range(degree_duration):
        cash_flows.append(annual_investment)

    # Post-Graduation Years
    # Starting salary ramps up to mid-career earnings around year 10 post-entry
    for yr in range(degree_duration + 1, horizon_years + 1):
        t = yr - degree_duration
        # Real wage growth modeling
        c_wage = college_earnings * ((1 + wage_growth_rate) ** (t - 6)) if t >= 6 else (college_earnings * 0.75 * ((1 + 0.04) ** t))
        hs_wage = hs_baseline * ((1 + 0.01) ** yr)
        premium = c_wage - hs_wage
        cash_flows.append(premium)

    # Discount cash flows
    npv = 0.0
    for t, cf in enumerate(cash_flows, start=1):
        npv += cf / ((1 + discount_rate) ** t)
        
    return npv


def calculate_payback_period(annual_net_cost: float, median_debt: float, 
                             college_earnings: float, hs_baseline: float, 
                             degree_duration: int = 4) -> float:
    """
    Calculates exact estimated payback period (break-even horizon in years)
    to recover net out-of-pocket costs, debt, and opportunity costs through earnings premium.
    """
    if pd.isna(annual_net_cost) or pd.isna(college_earnings) or pd.isna(hs_baseline):
        return np.nan

    earn_premium = college_earnings - hs_baseline
    if earn_premium <= 0:
        return np.nan # Never breaks even

    # Total investment = Cumulative 4-year net cost + foregone wages + median debt interest
    total_investment = (annual_net_cost * degree_duration) + (0.50 * hs_baseline * degree_duration) + (median_debt if pd.notna(median_debt) else 0)
    
    # Payback years post-grad + duration of degree
    payback_years = (total_investment / earn_premium) + degree_duration
    return round(payback_years, 2)


def compute_institution_roi_dataframe(df_inst: pd.DataFrame, hs_baseline: float) -> pd.DataFrame:
    """
    Computes comprehensive economic and ROI indicators across all institutions.
    """
    roi_df = df_inst.copy()

    # Total 4-Year Net Cost
    roi_df["total_4yr_net_cost"] = roi_df["annual_net_cost"] * 4

    # Earnings metrics
    roi_df["midcareer_earnings"] = roi_df["MD_EARN_WNE_P10"]
    roi_df["earlycareer_earnings"] = roi_df["MD_EARN_WNE_P6"]
    
    # Earnings Premiums
    roi_df["earn_premium_10yr"] = roi_df["midcareer_earnings"] - hs_baseline
    roi_df["earn_premium_6yr"] = roi_df["earlycareer_earnings"] - hs_baseline

    # Debt-Adjusted Net ROI Formula:
    # ROI = (MidCareerPay - (MedianDebt + 4 * AnnualNetCost)) / (4 * AnnualNetCost)
    cost_denom = roi_df["total_4yr_net_cost"].replace(0, np.nan)
    debt_val = roi_df["median_debt"].fillna(0)
    roi_df["roi_debt_adjusted"] = (roi_df["midcareer_earnings"] - (debt_val + roi_df["total_4yr_net_cost"])) / cost_denom

    # Annualized ROI percentage
    roi_df["roi_percentage"] = roi_df["roi_debt_adjusted"] * 100

    # Debt Burdens
    roi_df["debt_to_earnings_ratio"] = roi_df["median_debt"] / roi_df["midcareer_earnings"]
    roi_df["est_monthly_loan_payment"] = roi_df["median_debt"].apply(calculate_monthly_debt_payment)
    roi_df["debt_service_burden_pct"] = (roi_df["est_monthly_loan_payment"] * 12) / roi_df["midcareer_earnings"] * 100

    # Payback Period (Years)
    roi_df["payback_period_years"] = [
        calculate_payback_period(cost, debt, earn, hs_baseline)
        for cost, debt, earn in zip(roi_df["annual_net_cost"], roi_df["median_debt"], roi_df["midcareer_earnings"])
    ]

    # Net Present Values (10-year, 20-year, 30-year)
    roi_df["npv_10yr"] = [
        calculate_npv(cost, earn, hs_baseline, horizon_years=10, discount_rate=0.04)
        for cost, earn in zip(roi_df["annual_net_cost"], roi_df["midcareer_earnings"])
    ]
    roi_df["npv_20yr"] = [
        calculate_npv(cost, earn, hs_baseline, horizon_years=20, discount_rate=0.04)
        for cost, earn in zip(roi_df["annual_net_cost"], roi_df["midcareer_earnings"])
    ]
    roi_df["npv_30yr"] = [
        calculate_npv(cost, earn, hs_baseline, horizon_years=30, discount_rate=0.04)
        for cost, earn in zip(roi_df["annual_net_cost"], roi_df["midcareer_earnings"])
    ]

    # Clean out infs
    roi_df = roi_df.replace([np.inf, -np.inf], np.nan)
    return roi_df


def compute_major_roi_dataframe(df_fod: pd.DataFrame, hs_baseline: float) -> pd.DataFrame:
    """
    Computes major-level (Field of Study) earnings premiums and debt burdens.
    """
    if df_fod.empty:
        return pd.DataFrame()

    fod_df = df_fod.copy()
    
    # 4-Year post grad earnings as mid-career proxy, fallback to 1-yr
    fod_df["major_earnings"] = fod_df["EARN_MDN_4YR"].combine_first(fod_df["EARN_MDN_1YR"])
    fod_df["major_debt"] = fod_df["DEBT_ALL_STGP_EVAL_MDN"]
    
    fod_df["earn_premium"] = fod_df["major_earnings"] - hs_baseline
    fod_df["debt_to_earnings"] = fod_df["major_debt"] / fod_df["major_earnings"]
    
    # Estimated major payback period (assuming average annual net cost $15,000)
    fod_df["est_payback_years"] = [
        calculate_payback_period(15000.0, debt, earn, hs_baseline)
        for debt, earn in zip(fod_df["major_debt"], fod_df["major_earnings"])
    ]

    return fod_df
