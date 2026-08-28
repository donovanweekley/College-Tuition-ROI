"""
Econometric and Statistical Modeling Module
Implements:
  1. Heteroskedasticity-Robust OLS Regressions (HC3)
  2. Non-Parametric Bootstrapping for 95% Confidence Intervals
  3. K-Means Machine Learning Clustering for Institutional Value Segmentation
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def run_institutional_regressions(roi_df: pd.DataFrame) -> dict:
    """
    Fits econometric OLS regression models with HC3 robust standard errors
    to evaluate determinants of college ROI and earnings premiums.
    """
    clean_df = roi_df.dropna(subset=[
        "roi_debt_adjusted", "annual_net_cost", "median_debt", "midcareer_earnings"
    ]).copy()
    
    # Filter realistic values
    clean_df = clean_df[(clean_df["annual_net_cost"] > 1000) & (clean_df["median_debt"] > 500) & (clean_df["midcareer_earnings"] > 10000)]
    
    # One-hot encode categorical sector
    clean_df = pd.get_dummies(clean_df, columns=["sector"], drop_first=True, dtype=float)
    
    # Model 1: Determinants of ROI (Debt-Adjusted Net)
    # Log transforms for scale stabilization
    clean_df["log_cost"] = np.log(clean_df["annual_net_cost"])
    clean_df["log_debt"] = np.log(clean_df["median_debt"])
    clean_df["log_earnings"] = np.log(clean_df["midcareer_earnings"])
    
    # Sector dummy column names
    sector_cols = [c for c in clean_df.columns if c.startswith("sector_")]
    
    # Fill optional predictors
    clean_df["completion_rate_fill"] = clean_df["completion_rate"].fillna(clean_df["completion_rate"].median())
    clean_df["stem_share_fill"] = clean_df["stem_share"].fillna(0.0)
    
    features_m1 = ["log_cost", "log_debt", "completion_rate_fill", "stem_share_fill"] + sector_cols
    X1 = clean_df[features_m1]
    X1 = sm.add_constant(X1)
    y1 = clean_df["roi_debt_adjusted"]
    
    ols_roi = sm.OLS(y1, X1).fit(cov_type="HC3")
    
    # Model 2: Determinants of Log Mid-Career Earnings
    features_m2 = ["log_cost", "completion_rate_fill", "stem_share_fill"] + sector_cols
    if "ADM_RATE" in clean_df.columns:
        clean_df["adm_rate_fill"] = clean_df["ADM_RATE"].fillna(clean_df["ADM_RATE"].median())
        features_m2.append("adm_rate_fill")
        
    X2 = clean_df[features_m2]
    X2 = sm.add_constant(X2)
    y2 = clean_df["log_earnings"]
    
    ols_earnings = sm.OLS(y2, X2).fit(cov_type="HC3")

    return {
        "ols_roi": ols_roi,
        "ols_earnings": ols_earnings,
        "sample_size": len(clean_df),
        "clean_data": clean_df
    }


def compute_bootstrap_confidence_intervals(roi_df: pd.DataFrame, n_iterations: int = 2000, seed: int = 42) -> dict:
    """
    Computes non-parametric bootstrap 95% Confidence Intervals for key economic metrics across sectors.
    """
    rng = np.random.default_rng(seed)
    results = {}
    
    sectors = ["All"] + [s for s in roi_df["sector"].unique() if s != "Unknown"]
    
    for sector in sectors:
        if sector == "All":
            sub = roi_df.copy()
        else:
            sub = roi_df[roi_df["sector"] == sector]
            
        metrics_to_bootstrap = {
            "earn_premium_10yr": sub["earn_premium_10yr"].dropna().values,
            "roi_debt_adjusted": sub["roi_debt_adjusted"].dropna().values,
            "payback_period_years": sub["payback_period_years"].dropna().values,
            "npv_20yr": sub["npv_20yr"].dropna().values
        }
        
        sector_res = {}
        for metric_name, vals in metrics_to_bootstrap.items():
            if len(vals) < 30:
                continue
            boot_means = [np.mean(rng.choice(vals, size=len(vals), replace=True)) for _ in range(n_iterations)]
            sector_res[metric_name] = {
                "mean": float(np.mean(vals)),
                "ci_lower": float(np.percentile(boot_means, 2.5)),
                "ci_upper": float(np.percentile(boot_means, 97.5)),
                "sample_n": len(vals)
            }
        results[sector] = sector_res

    return results


def perform_institutional_clustering(roi_df: pd.DataFrame, n_clusters: int = 4, seed: int = 42) -> tuple[pd.DataFrame, KMeans, StandardScaler]:
    """
    Performs K-Means Machine Learning clustering to segment higher education institutions into value tiers.
    """
    feature_cols = ["annual_net_cost", "midcareer_earnings", "median_debt", "completion_rate"]
    cluster_df = roi_df.dropna(subset=feature_cols).copy()
    
    scaler = StandardScaler()
    scaled_feats = scaler.fit_transform(cluster_df[feature_cols])
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
    cluster_df["cluster_id"] = kmeans.fit_predict(scaled_feats)
    
    # Assign human-interpretable labels based on cluster characteristics
    cluster_summaries = cluster_df.groupby("cluster_id")[feature_cols].mean()
    
    # Sort clusters by earnings and completion rate to assign descriptive names
    sorted_clusters = cluster_summaries.sort_values(by="midcareer_earnings", ascending=False).index.tolist()
    
    label_map = {
        sorted_clusters[0]: "Elite & High-Return Flagships",
        sorted_clusters[1]: "Strong Value & Regional Anchors",
        sorted_clusters[2]: "High-Cost Moderate-Yield",
        sorted_clusters[3]: "High-Risk / Low-Completion"
    }
    
    cluster_df["cluster_label"] = cluster_df["cluster_id"].map(label_map)
    return cluster_df, kmeans, scaler
