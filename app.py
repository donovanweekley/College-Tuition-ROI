"""
Higher Education Return on Investment (ROI) Interactive Explorer
Author: Donovan Weekley (UIUC Economics & Data Science)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Higher Ed ROI & Payback Explorer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_app_data():
    base_dir = Path(__file__).resolve().parent
    tables_dir = base_dir / "outputs" / "tables"
    processed_dir = base_dir / "data" / "processed"
    
    inst_df = pd.read_parquet(processed_dir / "scorecard_institutions.parquet")
    fod_df = pd.read_parquet(processed_dir / "scorecard_field_of_study.parquet")
    roi_inst = pd.read_csv(tables_dir / "roi_institutions_full.csv")
    
    return inst_df, fod_df, roi_inst

inst_df, fod_df, roi_inst = load_app_data()

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/a/af/University_of_Illinois_seal.svg", width=80)
st.sidebar.title("Higher Ed ROI Explorer")
st.sidebar.markdown("**Author:** Donovan Weekley  \n*UIUC Economics & Data Science*")

mode = st.sidebar.radio("Navigation", ["Institution Benchmark", "Major / Field of Study", "Sector Econometrics", "Custom ROI Calculator"])

# --- TAB 1: INSTITUTION BENCHMARK ---
if mode == "Institution Benchmark":
    st.title("Higher Education Institutional ROI Benchmark")
    st.markdown("Analyze post-graduation financial outcomes, debt burdens, and payback horizons across **6,400+ U.S. colleges**.")
    
    # Institution selector
    col1, col2 = st.columns([3, 1])
    with col1:
        default_inst = "University of Illinois Urbana-Champaign" if "University of Illinois Urbana-Champaign" in roi_inst["INSTNM"].values else roi_inst["INSTNM"].iloc[0]
        all_schools = sorted(roi_inst["INSTNM"].dropna().unique())
        selected_school = st.selectbox("Select Institution:", all_schools, index=all_schools.index(default_inst) if default_inst in all_schools else 0)
    
    school_row = roi_inst[roi_inst["INSTNM"] == selected_school].iloc[0]
    
    # Metrics Banner
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Sector", str(school_row["sector"]))
    with m2:
        st.metric("Annual Net Price", f"${school_row['annual_net_cost']:,.0f}" if pd.notna(school_row['annual_net_cost']) else "N/A")
    with m3:
        st.metric("10-Yr Median Earnings", f"${school_row['midcareer_earnings']:,.0f}" if pd.notna(school_row['midcareer_earnings']) else "N/A")
    with m4:
        st.metric("Debt-Adjusted Net ROI", f"{school_row['roi_debt_adjusted']:.2f}x" if pd.notna(school_row['roi_debt_adjusted']) else "N/A")
    with m5:
        st.metric("Est. Payback Horizon", f"{school_row['payback_period_years']:.1f} yrs" if pd.notna(school_row['payback_period_years']) else "N/A")
        
    st.markdown("---")
    
    # Detailed plots
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Cumulative Net Present Value (NPV) Trajectory")
        npv_10 = school_row["npv_10yr"] if pd.notna(school_row["npv_10yr"]) else 0
        npv_20 = school_row["npv_20yr"] if pd.notna(school_row["npv_20yr"]) else 0
        npv_30 = school_row["npv_30yr"] if pd.notna(school_row["npv_30yr"]) else 0
        
        fig_npv = go.Figure(data=[
            go.Bar(name="NPV", x=["10-Year Horizon", "20-Year Horizon", "30-Year Horizon"], 
                   y=[npv_10, npv_20, npv_30], marker_color=["#1976d2", "#2e7d32", "#00796b"])
        ])
        fig_npv.update_layout(yaxis_title="Discounted Net Value ($)", yaxis_tickformat="$,.0f", template="plotly_white")
        st.plotly_chart(fig_npv, use_container_width=True)
        
    with c2:
        st.subheader("Financial Aid Net Price by Family Income Tier")
        raw_school = inst_df[inst_df["INSTNM"] == selected_school]
        if not raw_school.empty:
            r = raw_school.iloc[0]
            tiers = ["$0 - $30k", "$30k - $48k", "$48k - $75k", "$75k - $110k", "$110k+"]
            vals = [
                r.get("NPT41_PUB", np.nan) if pd.notna(r.get("NPT41_PUB")) else r.get("NPT41_PRIV", np.nan),
                r.get("NPT42_PUB", np.nan) if pd.notna(r.get("NPT42_PUB")) else r.get("NPT42_PRIV", np.nan),
                r.get("NPT43_PUB", np.nan) if pd.notna(r.get("NPT43_PUB")) else r.get("NPT43_PRIV", np.nan),
                r.get("NPT44_PUB", np.nan) if pd.notna(r.get("NPT44_PUB")) else r.get("NPT44_PRIV", np.nan),
                r.get("NPT45_PUB", np.nan) if pd.notna(r.get("NPT45_PUB")) else r.get("NPT45_PRIV", np.nan)
            ]
            fig_tiers = px.bar(x=tiers, y=vals, labels={"x": "Family Income Quintile", "y": "Annual Net Price ($)"},
                               color_discrete_sequence=["#f57c00"])
            fig_tiers.update_layout(yaxis_tickformat="$,.0f", template="plotly_white")
            st.plotly_chart(fig_tiers, use_container_width=True)
        else:
            st.info("Income tier breakdown not available.")

# --- TAB 2: MAJOR EXPLORER ---
elif mode == "Major / Field of Study":
    st.title("Major & Degree Program Financial Outcomes")
    st.markdown("Compare median earnings and debt burdens across undergraduate fields of study.")
    
    # Filter by school or major
    search_school = st.selectbox("Filter by School (Optional):", ["All Schools"] + sorted(fod_df["INSTNM"].dropna().unique()))
    
    if search_school != "All Schools":
        sub_fod = fod_df[(fod_df["INSTNM"] == search_school) & (fod_df["is_bachelors"])].copy()
    else:
        sub_fod = fod_df[fod_df["is_bachelors"]].copy()
        
    sub_clean = sub_fod.dropna(subset=["EARN_MDN_4YR"]).sort_values(by="EARN_MDN_4YR", ascending=False)
    
    st.dataframe(
        sub_clean[["INSTNM", "major_title", "EARN_MDN_1YR", "EARN_MDN_4YR", "DEBT_ALL_STGP_EVAL_MDN"]].rename(
            columns={
                "INSTNM": "Institution",
                "major_title": "Major / Field of Study",
                "EARN_MDN_1YR": "1-Yr Post-Grad Earnings ($)",
                "EARN_MDN_4YR": "4-Yr Post-Grad Earnings ($)",
                "DEBT_ALL_STGP_EVAL_MDN": "Median Student Debt ($)"
            }
        ).head(100),
        use_container_width=True
    )

# --- TAB 3: SECTOR ECONOMETRICS ---
elif mode == "Sector Econometrics":
    st.title("Econometric Regression & Sector Distribution")
    st.markdown("Macro distribution analysis and OLS regression elasticity modeling.")
    
    fig_scatter = px.scatter(
        roi_inst[(roi_inst["annual_net_cost"] > 2000) & (roi_inst["annual_net_cost"] < 60000) & (roi_inst["midcareer_earnings"] > 15000)],
        x="annual_net_cost",
        y="midcareer_earnings",
        color="sector",
        hover_name="INSTNM",
        trendline="ols",
        labels={"annual_net_cost": "Annual Net Cost ($)", "midcareer_earnings": "10-Year Median Earnings ($)"},
        title="Net Cost vs. 10-Year Mid-Career Earnings by Institutional Sector"
    )
    fig_scatter.update_layout(template="plotly_white")
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- TAB 4: CUSTOM CALCULATOR ---
elif mode == "Custom ROI Calculator":
    st.title("Personalized ROI & Payback Calculator")
    st.markdown("Customize your financial aid, expected degree duration, and loan parameters to model personalized return.")
    
    c1, c2 = st.columns(2)
    with c1:
        custom_net_cost = st.slider("Expected Annual Net Cost ($):", 0, 80000, 15000, step=1000)
        custom_debt = st.slider("Anticipated Student Debt at Graduation ($):", 0, 100000, 20000, step=2000)
        custom_earnings = st.slider("Expected Mid-Career Salary ($):", 30000, 200000, 75000, step=5000)
    with c2:
        custom_hs_wage = st.slider("High School Baseline Earnings ($):", 25000, 65000, 55400, step=1000)
        custom_discount = st.slider("Real Discount Rate (%):", 1.0, 10.0, 4.0, step=0.5) / 100.0
        custom_duration = st.slider("Years to Complete Degree:", 2, 6, 4)
        
    # Calculate custom ROI
    tot_cost = custom_net_cost * custom_duration
    tot_inv = tot_cost + custom_debt + (0.5 * custom_hs_wage * custom_duration)
    earn_prem = custom_earnings - custom_hs_wage
    custom_roi = (custom_earnings - (custom_debt + tot_cost)) / tot_cost if tot_cost > 0 else np.nan
    custom_payback = (tot_inv / earn_prem) + custom_duration if earn_prem > 0 else np.nan
    
    st.markdown("---")
    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("Personalized Debt-Adjusted Net ROI", f"{custom_roi:.2f}x" if pd.notna(custom_roi) else "N/A")
    with r2:
        st.metric("Estimated Payback Period", f"{custom_payback:.1f} years" if pd.notna(custom_payback) else "Negative Premium")
    with r3:
        st.metric("Annual Earnings Premium", f"+${earn_prem:,.0f}" if earn_prem > 0 else f"-${abs(earn_prem):,.0f}")
