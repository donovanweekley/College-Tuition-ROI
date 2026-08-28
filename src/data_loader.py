"""
Higher Education ROI Data Loader Pipeline
Aggregates multi-source public datasets:
  1. U.S. Department of Education College Scorecard (Institution-level)
  2. U.S. Department of Education College Scorecard (Field-of-Study/Major-level)
  3. U.S. Census Bureau Table P-24 (Educational Attainment Historical Earnings)
  4. U.S. Census Bureau ACS Field of Degree Tables (Tab2, Tab3, Tab6)
"""

import os
import zipfile
import re
import pandas as pd
import numpy as np
from pathlib import Path

# Paths configuration
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"


def extract_census_p24(filepath: Path = None) -> tuple[float, pd.DataFrame]:
    """
    Parses US Census Bureau Table P-24 (Historical Earnings by Educational Attainment).
    Extracts the modern inflation-adjusted High School diploma baseline median earnings.
    """
    if filepath is None:
        filepath = RAW_DATA_DIR / "p24.xlsx"

    if not filepath.exists():
        print(f"[Warning] {filepath} not found. Using default HS baseline $45,000.")
        return 45000.0, pd.DataFrame()

    try:
        # Read the raw sheet
        raw_df = pd.read_excel(filepath, sheet_name="p24", header=None)
        
        # Search for high school graduate median earnings row
        # Table P-24 contains sections: High school graduates, Some college, Bachelor's degree, etc.
        text_dump = raw_df.astype(str)
        
        # Look for High School graduate section
        hs_idx = -1
        for r in range(len(raw_df)):
            row_str = " ".join(text_dump.iloc[r].tolist()).lower()
            if "high school graduate" in row_str or "high school" in row_str:
                hs_idx = r
                break
        
        if hs_idx != -1:
            # Look in the window below for recent year median earnings
            sub = raw_df.iloc[hs_idx:hs_idx+25]
            nums = pd.to_numeric(sub.stack().astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce").dropna()
            valid_nums = nums[(nums >= 30000) & (nums <= 65000)]
            if len(valid_nums) > 0:
                hs_baseline = float(valid_nums.iloc[0]) # Most recent year
            else:
                hs_baseline = 45000.0
        else:
            # Global median heuristic for HS income
            nums = pd.to_numeric(raw_df.stack().astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce").dropna()
            valid_nums = nums[(nums >= 35000) & (nums <= 55000)]
            hs_baseline = float(valid_nums.median()) if len(valid_nums) > 0 else 45000.0

        print(f"[DataLoader] Successfully extracted Census P-24 HS Earnings Baseline: ${hs_baseline:,.2f}")
        return hs_baseline, raw_df

    except Exception as e:
        print(f"[Warning] Error parsing P-24: {e}. Falling back to $45,000 baseline.")
        return 45000.0, pd.DataFrame()


def load_acs_field_of_degree() -> pd.DataFrame:
    """
    Parses ACS Tab2_FOD.xlsx, Tab3_FOD.xlsx for field of degree median earnings.
    """
    tab2_path = RAW_DATA_DIR / "Tab2_FOD.xlsx"
    if not tab2_path.exists():
        print(f"[Warning] {tab2_path} not found.")
        return pd.DataFrame()

    try:
        df = pd.read_excel(tab2_path, skiprows=4)
        clean_rows = []
        current_category = "General"
        
        for idx, row in df.iterrows():
            field_name = str(row.iloc[0]).strip()
            if not field_name or field_name == "nan" or "Table" in field_name:
                continue
            
            val1 = row.iloc[1]
            if pd.isna(val1) or str(val1).strip() == "" or str(val1).strip() == "nan":
                current_category = field_name
                continue
                
            total_earn = pd.to_numeric(str(val1).replace(",", "").replace("$", ""), errors="coerce")
            if pd.notna(total_earn) and total_earn > 10000:
                clean_rows.append({
                    "broad_category": current_category,
                    "field_of_degree": field_name,
                    "median_earnings": total_earn
                })
                
        acs_df = pd.DataFrame(clean_rows)
        print(f"[DataLoader] Processed ACS Field of Degree benchmarks: {len(acs_df)} fields extracted.")
        return acs_df
    except Exception as e:
        print(f"[Warning] Error processing ACS tables: {e}")
        return pd.DataFrame()


def load_scorecard_institutions(force_recompute: bool = False) -> pd.DataFrame:
    """
    Extracts and cleans institution-level College Scorecard data directly from zip.
    Caches processed dataset as Parquet for fast reload.
    """
    cache_path = PROCESSED_DATA_DIR / "scorecard_institutions.parquet"
    if cache_path.exists() and not force_recompute:
        print(f"[DataLoader] Loading cached institution data from {cache_path}")
        return pd.read_parquet(cache_path)

    zip_path = RAW_DATA_DIR / "Most-Recent-Cohorts-Institution_05192025.zip"
    if not zip_path.exists():
        zips = list(RAW_DATA_DIR.glob("*Institution*.zip"))
        if zips:
            zip_path = zips[0]
        else:
            raise FileNotFoundError(f"Scorecard Institution zip file not found in {RAW_DATA_DIR}")

    print(f"[DataLoader] Reading College Scorecard Institutions from {zip_path.name}...")
    
    cols_to_use = [
        "UNITID", "OPEID6", "INSTNM", "CITY", "STABBR", "ZIP", "CONTROL", 
        "ADM_RATE", "SAT_AVG", "UGDS", "COSTT4_A", "COSTT4_P", 
        "TUITIONFEE_IN", "TUITIONFEE_OUT", "NPT4_PUB", "NPT4_PRIV",
        "NPT41_PUB", "NPT42_PUB", "NPT43_PUB", "NPT44_PUB", "NPT45_PUB",
        "NPT41_PRIV", "NPT42_PRIV", "NPT43_PRIV", "NPT44_PRIV", "NPT45_PRIV",
        "C150_4", "C150_L4", "GRAD_DEBT_MDN", "GRAD_DEBT_MDN_SUPP",
        "MD_EARN_WNE_P6", "MD_EARN_WNE_P10", "PCT10_EARN_WNE_P10", 
        "PCT25_EARN_WNE_P10", "PCT75_EARN_WNE_P10", "PCT90_EARN_WNE_P10",
        "RPY_3YR_RT", "RPY_5YR_RT", "PCIP11", "PCIP14", "PCIP52"
    ]

    with zipfile.ZipFile(zip_path) as z:
        csv_files = [f for f in z.namelist() if f.endswith(".csv")]
        if not csv_files:
            raise ValueError(f"No CSV file found in {zip_path}")
        
        target_csv = csv_files[0]
        with z.open(target_csv) as f:
            header = pd.read_csv(f, nrows=1)
            available_cols = [c for c in cols_to_use if c in header.columns]
            f.seek(0)
            df = pd.read_csv(f, usecols=available_cols, low_memory=False, na_values=["PrivacySuppressed", "NULL", "NaN", "nan"])

    print(f"[DataLoader] Raw institution dataset shape: {df.shape}")

    # Standardize column types and values
    df["UNITID"] = pd.to_numeric(df["UNITID"], errors="coerce")
    df["INSTNM"] = df["INSTNM"].astype(str)
    
    # Map Sector / Control
    control_map = {1: "Public", 2: "Private Nonprofit", 3: "Private For-Profit"}
    df["sector"] = df["CONTROL"].map(control_map).fillna("Unknown")

    # Clean numeric financial & outcome variables
    numeric_cols = [
        "ADM_RATE", "SAT_AVG", "UGDS", "COSTT4_A", "COSTT4_P", "TUITIONFEE_IN", "TUITIONFEE_OUT",
        "NPT4_PUB", "NPT4_PRIV", "C150_4", "C150_L4", "GRAD_DEBT_MDN", "GRAD_DEBT_MDN_SUPP",
        "MD_EARN_WNE_P6", "MD_EARN_WNE_P10", "PCT10_EARN_WNE_P10", "PCT25_EARN_WNE_P10",
        "PCT75_EARN_WNE_P10", "PCT90_EARN_WNE_P10", "RPY_3YR_RT", "RPY_5YR_RT",
        "PCIP11", "PCIP14", "PCIP52"
    ]
    
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Unified Annual Net Cost (NPT4_PUB for public, NPT4_PRIV for private, fallback to COSTT4_A or TUITIONFEE_IN)
    df["annual_net_cost"] = df["NPT4_PUB"].combine_first(df["NPT4_PRIV"]).combine_first(df["COSTT4_A"]).combine_first(df["TUITIONFEE_IN"])
    
    # Unified Median Debt (combine GRAD_DEBT_MDN and GRAD_DEBT_MDN_SUPP)
    debt_col = df["GRAD_DEBT_MDN"].combine_first(df["GRAD_DEBT_MDN_SUPP"]) if "GRAD_DEBT_MDN_SUPP" in df.columns else df["GRAD_DEBT_MDN"]
    df["median_debt"] = debt_col
    
    # Unified Completion Rate (4-year and Less-than-4-year)
    df["completion_rate"] = df["C150_4"].combine_first(df["C150_L4"])
    
    # STEM Degree Share (Computer Science + Engineering)
    cs_share = df["PCIP11"].fillna(0) if "PCIP11" in df.columns else 0
    eng_share = df["PCIP14"].fillna(0) if "PCIP14" in df.columns else 0
    df["stem_share"] = cs_share + eng_share

    # Save to parquet cache
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path, index=False)
    print(f"[DataLoader] Cached clean institution dataset to {cache_path}")
    return df


def load_scorecard_field_of_study(force_recompute: bool = False) -> pd.DataFrame:
    """
    Extracts and cleans Field of Study (Major) College Scorecard data directly from zip.
    Caches processed dataset as Parquet for fast reload.
    """
    cache_path = PROCESSED_DATA_DIR / "scorecard_field_of_study.parquet"
    if cache_path.exists() and not force_recompute:
        print(f"[DataLoader] Loading cached field of study data from {cache_path}")
        return pd.read_parquet(cache_path)

    zip_path = RAW_DATA_DIR / "Most-Recent-Cohorts-Field-of-Study_04172025.zip"
    if not zip_path.exists():
        zips = list(RAW_DATA_DIR.glob("*Field-of-Study*.zip"))
        if zips:
            zip_path = zips[0]
        else:
            print(f"[Warning] Scorecard Field of Study zip not found in {RAW_DATA_DIR}")
            return pd.DataFrame()

    print(f"[DataLoader] Reading College Scorecard Field-of-Study from {zip_path.name}...")

    cols_to_use = [
        "UNITID", "OPEID6", "INSTNM", "CONTROL", "MAIN", "CIPCODE", "CIPDESC",
        "CREDLEV", "CREDDESC", "DEBT_ALL_STGP_EVAL_MDN", "DEBT_ALL_STGP_EVAL_MEAN",
        "EARN_MDN_1YR", "EARN_MDN_4YR", "EARN_MDN_5YR"
    ]

    with zipfile.ZipFile(zip_path) as z:
        csv_files = [f for f in z.namelist() if f.endswith(".csv")]
        if not csv_files:
            return pd.DataFrame()
        
        target_csv = csv_files[0]
        with z.open(target_csv) as f:
            header = pd.read_csv(f, nrows=1)
            available_cols = [c for c in cols_to_use if c in header.columns]
            f.seek(0)
            df = pd.read_csv(f, usecols=available_cols, low_memory=False, na_values=["PrivacySuppressed", "NULL", "NaN", "nan"])

    print(f"[DataLoader] Raw field of study dataset shape: {df.shape}")

    # Clean numeric fields
    for c in ["DEBT_ALL_STGP_EVAL_MDN", "DEBT_ALL_STGP_EVAL_MEAN", "EARN_MDN_1YR", "EARN_MDN_4YR", "EARN_MDN_5YR"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Map Sector
    control_map = {1: "Public", 2: "Private Nonprofit", 3: "Private For-Profit"}
    df["sector"] = df["CONTROL"].map(control_map).fillna("Unknown")

    # Filter to Bachelor's Degrees (CREDLEV == 3) for primary comparison, while keeping all available
    df["is_bachelors"] = df["CREDLEV"] == 3

    # Clean Major Title
    df["major_title"] = df["CIPDESC"].astype(str).str.replace(r"\.$", "", regex=True)

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path, index=False)
    print(f"[DataLoader] Cached clean field of study dataset to {cache_path}")
    return df


def load_all_datasets(force_recompute: bool = False):
    """
    Master data loader function returning all cleansed datasets and benchmarks.
    """
    hs_baseline, p24_raw = extract_census_p24()
    acs_fod = load_acs_field_of_degree()
    df_inst = load_scorecard_institutions(force_recompute=force_recompute)
    df_fod = load_scorecard_field_of_study(force_recompute=force_recompute)

    return {
        "hs_baseline": hs_baseline,
        "p24_raw": p24_raw,
        "acs_fod": acs_fod,
        "institutions": df_inst,
        "field_of_study": df_fod
    }


if __name__ == "__main__":
    print("Testing Higher Education ROI Data Loader Pipeline...")
    data = load_all_datasets(force_recompute=True)
    print(f"Data loading complete!")
    print(f"  Institutions count: {len(data['institutions']):,}")
    print(f"  Field of Study records: {len(data['field_of_study']):,}")
    print(f"  ACS Majors count: {len(data['acs_fod']):,}")
    print(f"  Census HS Baseline: ${data['hs_baseline']:,.2f}")
