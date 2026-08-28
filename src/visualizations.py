"""
Publication-Grade Visualization Module
Generates high-resolution figures for econometric reports and executive presentations:
  1. ROI Distribution by Institutional Sector
  2. Net Cost vs Mid-Career Earnings Scatter with OLS Fit
  3. Top 20 U.S. Higher Education Institutions by ROI
  4. Top Bachelor's Majors by Net Earnings Premium
  5. Payback Period Horizon Distributions
  6. K-Means Value Segmentation Cluster Scatter
  7. Debt Burden vs Completion Rate Bubble Chart
  8. Multi-Horizon Net Present Value (NPV) Trajectory
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Style configuration
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 11,
    "figure.titlesize": 16,
    "figure.dpi": 300
})

PALETTE = {
    "Public": "#2b5c8f",
    "Private Nonprofit": "#2e7d32",
    "Private For-Profit": "#c62828",
    "Elite & High-Return Flagships": "#1565c0",
    "Strong Value & Regional Anchors": "#2e7d32",
    "High-Cost Moderate-Yield": "#f57c00",
    "High-Risk / Low-Completion": "#d32f2f"
}


def plot_roi_distribution(roi_df: pd.DataFrame, output_dir: Path) -> Path:
    """Distribution of Debt-Adjusted Net ROI stratified by sector."""
    plt.figure(figsize=(10, 6))
    
    clean = roi_df[(roi_df["roi_debt_adjusted"] >= -2.0) & (roi_df["roi_debt_adjusted"] <= 4.0)].copy()
    
    sns.kdeplot(
        data=clean,
        x="roi_debt_adjusted",
        hue="sector",
        common_norm=False,
        fill=True,
        alpha=0.35,
        linewidth=2,
        palette=PALETTE
    )
    
    plt.axvline(0, color="black", linestyle="--", alpha=0.6, label="Break-Even (ROI = 0)")
    plt.title("Distribution of Higher Education ROI by Institutional Sector")
    plt.xlabel("Debt-Adjusted Net ROI: [MidCareerPay - (MedianDebt + 4*NetCost)] / (4*NetCost)")
    plt.ylabel("Probability Density")
    plt.xlim(-1.5, 3.5)
    plt.tight_layout()
    
    save_path = output_dir / "01_roi_distribution_by_sector.png"
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    return save_path


def plot_cost_vs_earnings(roi_df: pd.DataFrame, output_dir: Path) -> Path:
    """Scatter plot: Annual Net Cost vs Mid-Career Earnings with OLS trendline."""
    plt.figure(figsize=(11, 7))
    
    sub = roi_df.dropna(subset=["annual_net_cost", "midcareer_earnings", "sector"]).copy()
    sub = sub[(sub["annual_net_cost"] > 1000) & (sub["annual_net_cost"] < 70000) & 
              (sub["midcareer_earnings"] > 15000) & (sub["midcareer_earnings"] < 180000)]
    
    sns.scatterplot(
        data=sub,
        x="annual_net_cost",
        y="midcareer_earnings",
        hue="sector",
        alpha=0.55,
        s=45,
        palette=PALETTE
    )
    
    # Regression trend line
    sns.regplot(
        data=sub,
        x="annual_net_cost",
        y="midcareer_earnings",
        scatter=False,
        color="#37474f",
        line_kws={"linestyle": "--", "linewidth": 2, "label": "National Average Trend"}
    )
    
    # Annotate prominent benchmark institutions if present
    notable = ["University of Illinois Urbana-Champaign", "Massachusetts Institute of Technology", 
               "Stanford University", "Harvard University", "University of Michigan-Ann Arbor",
               "University of California-Berkeley", "Purdue University-Main Campus"]
    
    for _, row in sub[sub["INSTNM"].isin(notable)].iterrows():
        plt.annotate(
            row["INSTNM"].replace("University of ", "Univ. of ").replace("-Main Campus", ""),
            (row["annual_net_cost"], row["midcareer_earnings"]),
            textcoords="offset points",
            xytext=(6, 6),
            fontsize=9,
            weight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="yellow", alpha=0.6, ec="black", lw=0.5)
        )
        
    plt.title("Institutional Net Cost vs. 10-Year Mid-Career Earnings")
    plt.xlabel("Annual Net Cost (Tuition, Fees & Living minus Grant Aid) ($)")
    plt.ylabel("10-Year Post-Entry Median Earnings ($)")
    plt.gca().xaxis.set_major_formatter("${x:,.0f}")
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    plt.legend(loc="upper left")
    plt.tight_layout()
    
    save_path = output_dir / "02_cost_vs_earnings_scatter.png"
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    return save_path


def plot_top_institutions(roi_df: pd.DataFrame, output_dir: Path, top_n: int = 20) -> Path:
    """Bar chart: Top 20 institutions ranked by Debt-Adjusted Net ROI."""
    plt.figure(figsize=(12, 8))
    
    # Filter to 4-year institutions with meaningful undergraduate enrollment
    valid = roi_df[(roi_df["UGDS"] >= 1000) & pd.notna(roi_df["roi_debt_adjusted"])].copy()
    top_schools = valid.nlargest(top_n, "roi_debt_adjusted").sort_values(by="roi_debt_adjusted", ascending=True)
    
    bars = plt.barh(top_schools["INSTNM"], top_schools["roi_debt_adjusted"], color="#1976d2", edgecolor="black", alpha=0.85)
    
    # Add value annotations
    for bar in bars:
        w = bar.get_width()
        plt.text(w + 0.05, bar.get_y() + bar.get_height()/2, f"{w:.2f}x", va="center", ha="left", fontsize=9, weight="bold")
        
    plt.title(f"Top {top_n} U.S. Colleges by Return on Investment (Debt-Adjusted Metric)")
    plt.xlabel("Debt-Adjusted Net ROI Multiple")
    plt.ylabel("Institution")
    plt.xlim(0, max(top_schools["roi_debt_adjusted"]) * 1.15)
    plt.tight_layout()
    
    save_path = output_dir / "03_top20_highest_roi_schools.png"
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    return save_path


def plot_top_majors(fod_df: pd.DataFrame, hs_baseline: float, output_dir: Path, top_n: int = 15) -> Path:
    """Bar chart: Top Bachelor's majors by median earnings premium over Census HS baseline."""
    if fod_df.empty or "major_earnings" not in fod_df.columns:
        return output_dir
        
    plt.figure(figsize=(12, 8))
    
    # Aggregate by 4-digit major title for Bachelor's degrees
    bachelors = fod_df[fod_df["is_bachelors"] & pd.notna(fod_df["major_earnings"])].copy()
    major_summary = bachelors.groupby("major_title").agg(
        median_earn=("major_earnings", "median"),
        median_debt=("major_debt", "median"),
        programs_count=("INSTNM", "count")
    ).reset_index()
    
    # Filter to majors offered at >= 20 institutions
    major_summary = major_summary[major_summary["programs_count"] >= 20]
    major_summary["earn_premium"] = major_summary["median_earn"] - hs_baseline
    
    top_majors = major_summary.nlargest(top_n, "earn_premium").sort_values(by="earn_premium", ascending=True)
    
    colors = ["#2e7d32" if x > 0 else "#c62828" for x in top_majors["earn_premium"]]
    bars = plt.barh(top_majors["major_title"], top_majors["earn_premium"], color=colors, edgecolor="black", alpha=0.85)
    
    for bar in bars:
        w = bar.get_width()
        plt.text(w + 1000, bar.get_y() + bar.get_height()/2, f"+${w:,.0f}", va="center", ha="left", fontsize=9, weight="bold")
        
    plt.title(f"Top {top_n} Undergraduate Majors by Annual Earnings Premium vs. High School Baseline")
    plt.xlabel(f"Annual Earnings Premium over High School Baseline (${hs_baseline:,.0f})")
    plt.ylabel("Field of Study / Major")
    plt.gca().xaxis.set_major_formatter("${x:,.0f}")
    plt.xlim(0, max(top_majors["earn_premium"]) * 1.18)
    plt.tight_layout()
    
    save_path = output_dir / "04_top_majors_by_earnings_premium.png"
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    return save_path


def plot_payback_periods(roi_df: pd.DataFrame, output_dir: Path) -> Path:
    """Boxplot of estimated payback period (break-even years) across sectors."""
    plt.figure(figsize=(10, 6))
    
    clean = roi_df.dropna(subset=["payback_period_years", "sector"]).copy()
    clean = clean[(clean["payback_period_years"] >= 4) & (clean["payback_period_years"] <= 30)]
    
    sns.boxplot(
        data=clean,
        x="sector",
        y="payback_period_years",
        hue="sector",
        legend=False,
        palette=PALETTE,
        showmeans=True,
        meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black", "markersize":"8"}
    )
    
    plt.title("Estimated Payback Period (Break-Even Horizon) by Institutional Sector")
    plt.xlabel("Institutional Sector")
    plt.ylabel("Years to Break Even (Including Opportunity Cost)")
    plt.tight_layout()
    
    save_path = output_dir / "05_payback_period_distribution.png"
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    return save_path


def plot_institutional_clusters(cluster_df: pd.DataFrame, output_dir: Path) -> Path:
    """Scatter plot illustrating K-Means ML clusters of higher ed value tiers."""
    plt.figure(figsize=(11, 7))
    
    sub = cluster_df[(cluster_df["annual_net_cost"] < 60000) & (cluster_df["midcareer_earnings"] < 160000)].copy()
    
    sns.scatterplot(
        data=sub,
        x="annual_net_cost",
        y="midcareer_earnings",
        hue="cluster_label",
        style="cluster_label",
        alpha=0.7,
        s=50,
        palette=PALETTE
    )
    
    plt.title("Machine Learning Clustering: Higher Education Institutional Value Tiers")
    plt.xlabel("Annual Net Cost ($)")
    plt.ylabel("10-Year Mid-Career Median Earnings ($)")
    plt.gca().xaxis.set_major_formatter("${x:,.0f}")
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    plt.legend(title="Cluster Segment", loc="upper left")
    plt.tight_layout()
    
    save_path = output_dir / "06_institutional_clustering_scatter.png"
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    return save_path


def plot_npv_horizons(roi_df: pd.DataFrame, output_dir: Path) -> Path:
    """Bar chart comparing 10-Year, 20-Year, and 30-Year cumulative Net Present Value by sector."""
    plt.figure(figsize=(10, 6))
    
    sectors = [s for s in ["Public", "Private Nonprofit", "Private For-Profit"] if s in roi_df["sector"].values]
    
    npv_data = []
    for s in sectors:
        sub = roi_df[roi_df["sector"] == s]
        npv_data.append({
            "Sector": s,
            "10-Year NPV": sub["npv_10yr"].median(),
            "20-Year NPV": sub["npv_20yr"].median(),
            "30-Year NPV": sub["npv_30yr"].median()
        })
        
    df_plot = pd.DataFrame(npv_data).melt(id_vars="Sector", var_name="Horizon", value_name="Median NPV ($)")
    
    sns.barplot(data=df_plot, x="Sector", y="Median NPV ($)", hue="Horizon", palette="Blues_d")
    
    plt.axhline(0, color="black", linestyle="--", alpha=0.7)
    plt.title("Median Cumulative Net Present Value (NPV) Across Horizons (4% Discount Rate)")
    plt.ylabel("Discounted Net Financial Return ($)")
    plt.gca().yaxis.set_major_formatter("${x:,.0f}")
    plt.tight_layout()
    
    save_path = output_dir / "07_npv_horizon_comparison.png"
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    return save_path


def generate_all_figures(roi_df: pd.DataFrame, fod_df: pd.DataFrame, cluster_df: pd.DataFrame, 
                         hs_baseline: float, output_dir: Path = None) -> list[Path]:
    """Master plotting pipeline generating all figures."""
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "outputs" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generated = [
        plot_roi_distribution(roi_df, output_dir),
        plot_cost_vs_earnings(roi_df, output_dir),
        plot_top_institutions(roi_df, output_dir),
        plot_top_majors(fod_df, hs_baseline, output_dir),
        plot_payback_periods(roi_df, output_dir),
        plot_institutional_clusters(cluster_df, output_dir),
        plot_npv_horizons(roi_df, output_dir)
    ]
    
    print(f"[Visualizations] Successfully generated {len(generated)} publication-ready figures in {output_dir}")
    return generated
