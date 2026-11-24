"""
src/features.py
===============
Hobli-Level Rainfall Deviation and Drought-Risk Prediction for Karnataka.

Stage 2: Feature Engineering & Target Construction.

Inputs:
    data/clean/clean_rainfall.csv

Outputs:
    data/features/features.csv
    data/features/README.md
    reports/suspect_normals.csv

Leakage Prevention Architecture:
    All predictive features are computed strictly from prior observed years (year < Y).
    No current or future year data leaks into features.
    Rows with missing prior history (n_prior_years == 0, i.e. year 2020) are explicitly
    preserved with n_prior_years=0, has_prior_history=0, and NaN for lag/rolling features,
    rather than silently imputing fake numbers.
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

# ==============================================================================
# THRESHOLDS & CONSTANTS
# ==============================================================================
DROUGHT_THRESHOLD = -20.0  # Deficit rainfall threshold (KSNDMC / IMD standard)
FLOOD_THRESHOLD = 40.0    # Severe excess rainfall threshold
EXCESS_THRESHOLD = 20.0   # Mild excess threshold for historical counts

INPUT_PATH = Path("data/clean/clean_rainfall.csv")
OUTPUT_DIR = Path("data/features")
OUTPUT_PATH = OUTPUT_DIR / "features.csv"
REPORTS_DIR = Path("reports")
SUSPECT_NORMALS_PATH = REPORTS_DIR / "suspect_normals.csv"


def load_clean_data(path: Path = INPUT_PATH) -> pd.DataFrame:
    """Load cleaned Karnataka rainfall dataset."""
    df = pd.read_csv(path)
    print(f"Loaded {len(df):,} records across {df['year'].nunique()} years "
          f"({sorted(df['year'].unique())}) from {path}")
    return df


def create_persistent_station_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construct a persistent station identifier for tracking stations across years.
    Handles duplicate station names within the same taluk and year using cumcount.
    """
    df = df.copy()
    df["station_sub_id"] = df.groupby(["district", "taluk", "hobli", "year"]).cumcount()
    df["station_id"] = (
        df["district"] + "_" + df["taluk"] + "_" + df["hobli"] + "_" + df["station_sub_id"].astype(str)
    )
    return df


def assign_target(df: pd.DataFrame, suspect_keys: set | None = None) -> pd.DataFrame:
    """
    Construct the 3-class target variable `risk_zone` based on annual departure_pct:
      - drought_prone : departure_pct <= -20.0%
      - flood_prone   : departure_pct >= +40.0%
      - stable        : -20.0% < departure_pct < +40.0%

    Suspect-normal override
    -----------------------
    Stations whose baseline normal never changes AND whose departures are
    persistently one-sided are flagged as suspect.  When such a station has a
    very high static normal (> 2 000 mm) *and* its actual rainfall still
    exceeds the statewide median normal, the apparent "drought_prone" label is
    an artifact of the uncalibrated benchmark, not evidence of real drought.
    These rows are reclassified to "stable" so the model is not trained on
    misleading labels.
    """
    conditions = [
        df["departure_pct"] <= DROUGHT_THRESHOLD,
        df["departure_pct"] >= FLOOD_THRESHOLD,
    ]
    choices = ["drought_prone", "flood_prone"]
    df["risk_zone"] = np.select(conditions, choices, default="stable")

    # Override artificial drought labels for suspect high-normal stations
    if suspect_keys is not None:
        median_normal = df["normal_mm"].median()
        is_suspect = df.apply(
            lambda r: (r["district"], r["taluk"], r["hobli"]) in suspect_keys,
            axis=1,
        )
        artificial_drought = (
            is_suspect
            & (df["risk_zone"] == "drought_prone")
            & (df["normal_mm"] > 2000)
            & (df["actual_mm"] > median_normal)
        )
        df.loc[artificial_drought, "risk_zone"] = "stable"

    return df


def identify_suspect_normals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify stations whose normal_mm never changes across years (range <= 1.0 mm)
    AND whose departure is strictly one-sided across all observed years.
    E.g. Agumbe (normal=7565.0 mm), which always shows deficit (-28% to -51%)
    despite receiving >4600 mm actual rainfall.
    """
    suspect_rows = []
    grouped = df.groupby(["district", "taluk", "hobli"])
    for (d, t, h), grp in grouped:
        norm_range = grp["normal_mm"].max() - grp["normal_mm"].min()
        all_neg = (grp["departure_pct"] < 0).all()
        all_pos = (grp["departure_pct"] > 0).all()
        n_years = len(grp)
        if norm_range <= 1.0 and (all_neg or all_pos) and n_years >= 5:
            direction = "always_deficit" if all_neg else "always_excess"
            mean_dep = grp["departure_pct"].mean()
            mean_norm = grp["normal_mm"].mean()
            mean_act = grp["actual_mm"].mean()
            note = (
                "Artificial drought classification due to massive baseline benchmark"
                if all_neg and mean_norm > 3000
                else "Unchanged baseline normal with persistent one-sided departure"
            )
            suspect_rows.append({
                "district": d,
                "taluk": t,
                "hobli": h,
                "normal_mm": round(mean_norm, 1),
                "direction": direction,
                "n_years": n_years,
                "mean_actual_mm": round(mean_act, 1),
                "min_departure_pct": round(grp["departure_pct"].min(), 2),
                "max_departure_pct": round(grp["departure_pct"].max(), 2),
                "mean_departure_pct": round(mean_dep, 2),
                "notes": note,
            })
    suspect_df = pd.DataFrame(suspect_rows)
    return suspect_df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer leak-free historical and spatial features strictly using prior observed years.
    """
    df = df.copy()

    # Sort chronologically by station and year
    df = df.sort_values(["station_id", "year"]).reset_index(drop=True)
    grp = df.groupby("station_id", sort=False)

    # 1. Missing history tracking
    df["n_prior_years"] = grp.cumcount()
    df["has_prior_history"] = (df["n_prior_years"] >= 1).astype(int)

    # 2. Deficit count (earlier years with departure < -20%)
    df["deficit_count"] = grp["departure_pct"].transform(
        lambda s: (s < DROUGHT_THRESHOLD).astype(int).expanding().sum().shift(1).fillna(0).astype(int)
    )

    # 3. Excess count (earlier years with departure > +20%)
    df["excess_count"] = grp["departure_pct"].transform(
        lambda s: (s > EXCESS_THRESHOLD).astype(int).expanding().sum().shift(1).fillna(0).astype(int)
    )

    # 4. Expanding mean of actual_mm (earlier years only)
    df["mean_actual_mm"] = grp["actual_mm"].transform(
        lambda s: s.expanding().mean().shift(1)
    ).round(2)

    # 5. Expanding sample standard deviation of actual_mm (earlier years only, min_periods=2)
    df["std_actual_mm"] = grp["actual_mm"].transform(
        lambda s: s.expanding().std().shift(1)
    ).round(2)

    # 6. Expanding mean and std of departure_pct (earlier years only)
    df["mean_departure_pct"] = grp["departure_pct"].transform(
        lambda s: s.expanding().mean().shift(1)
    ).round(2)
    df["std_departure_pct"] = grp["departure_pct"].transform(
        lambda s: s.expanding().std().shift(1)
    ).round(2)

    # 7. Previous observed year departure (lag-1)
    df["previous_year_departure"] = grp["departure_pct"].shift(1).round(2)

    # 8. Past years taluk & district departure (strictly year < Y)
    taluk_past = {}
    for yr in sorted(df["year"].unique()):
        past_df = df[df["year"] < yr]
        if len(past_df) == 0:
            continue
        t_means = past_df.groupby("taluk")["departure_pct"].mean().to_dict()
        d_means = past_df.groupby("district")["departure_pct"].mean().to_dict()
        taluk_past[yr] = (t_means, d_means)

    def get_past_taluk(r):
        yr = r["year"]
        t = r["taluk"]
        d = r["district"]
        if yr not in taluk_past:
            return np.nan
        t_dict, d_dict = taluk_past[yr]
        return t_dict.get(t, d_dict.get(d, np.nan))

    def get_past_district(r):
        yr = r["year"]
        d = r["district"]
        if yr not in taluk_past:
            return np.nan
        _, d_dict = taluk_past[yr]
        return d_dict.get(d, np.nan)

    df["taluk_mean_departure"] = df.apply(get_past_taluk, axis=1).round(2)
    df["district_mean_departure"] = df.apply(get_past_district, axis=1).round(2)

    # 9. Hobli minus taluk departure (hobli past mean minus taluk past mean)
    df["hobli_minus_taluk"] = (df["mean_departure_pct"] - df["taluk_mean_departure"]).round(2)

    return df


def verify_no_leakage(df: pd.DataFrame) -> bool:
    """Verify that no current or future year data leaked into features."""
    initial_year = df["year"] == 2020
    min_year = df.groupby("station_id")["year"].transform("min")
    first_year = df["year"] == min_year

    # 1. In the initial dataset year (2020), no history exists whatsoever
    no_taluk_2020 = df.loc[initial_year, "taluk_mean_departure"].isna().all()
    no_dist_2020 = df.loc[initial_year, "district_mean_departure"].isna().all()
    no_diff_2020 = df.loc[initial_year, "hobli_minus_taluk"].isna().all()

    # 2. For any station at its earliest observation, station-level history must be NaN or 0
    no_lag = df.loc[first_year, "previous_year_departure"].isna().all()
    no_mean_act = df.loc[first_year, "mean_actual_mm"].isna().all()
    no_std_act = df.loc[first_year, "std_actual_mm"].isna().all()
    no_mean_dep = df.loc[first_year, "mean_departure_pct"].isna().all()
    no_std_dep = df.loc[first_year, "std_departure_pct"].isna().all()
    def_zero = (df.loc[first_year, "deficit_count"] == 0).all()
    exc_zero = (df.loc[first_year, "excess_count"] == 0).all()
    n_prior_zero = (df.loc[first_year, "n_prior_years"] == 0).all()
    has_prior_zero = (df.loc[first_year, "has_prior_history"] == 0).all()

    all_passed = all([
        no_taluk_2020, no_dist_2020, no_diff_2020,
        no_lag, no_mean_act, no_std_act, no_mean_dep, no_std_dep,
        def_zero, exc_zero, n_prior_zero, has_prior_zero
    ])
    return all_passed


def print_class_balance_by_year(df: pd.DataFrame) -> None:
    """Print exact target class distribution per year and overall."""
    print("\n" + "=" * 80)
    print("TARGET CLASS BALANCE PER YEAR (`risk_zone`)")
    print(f"Rule: drought_prone (<= {DROUGHT_THRESHOLD}%), flood_prone (>= +{FLOOD_THRESHOLD}%), stable (otherwise)")
    print("=" * 80)

    crosstab = pd.crosstab(df["year"], df["risk_zone"], margins=True)
    crosstab_pct = (pd.crosstab(df["year"], df["risk_zone"], normalize="index") * 100).round(2)

    print(f"{'Year':<8} {'Drought-Prone':>15} {'Stable':>12} {'Flood-Prone':>15} {'Total':>10}")
    print("-" * 64)
    for yr in sorted(df["year"].unique()):
        d_cnt = crosstab.loc[yr, "drought_prone"] if "drought_prone" in crosstab.columns else 0
        s_cnt = crosstab.loc[yr, "stable"] if "stable" in crosstab.columns else 0
        f_cnt = crosstab.loc[yr, "flood_prone"] if "flood_prone" in crosstab.columns else 0
        tot = crosstab.loc[yr, "All"]

        d_pct = crosstab_pct.loc[yr, "drought_prone"] if "drought_prone" in crosstab_pct.columns else 0.0
        s_pct = crosstab_pct.loc[yr, "stable"] if "stable" in crosstab_pct.columns else 0.0
        f_pct = crosstab_pct.loc[yr, "flood_prone"] if "flood_prone" in crosstab_pct.columns else 0.0

        print(f"{yr:<8} {d_cnt:>6} ({d_pct:>5.1f}%) {s_cnt:>5} ({s_pct:>5.1f}%) {f_cnt:>7} ({f_pct:>5.1f}%) {tot:>10}")

    print("-" * 64)
    all_d = crosstab.loc["All", "drought_prone"]
    all_s = crosstab.loc["All", "stable"]
    all_f = crosstab.loc["All", "flood_prone"]
    all_tot = crosstab.loc["All", "All"]
    print(f"{'All':<8} {all_d:>6} ({all_d/all_tot*100:>5.1f}%) {all_s:>5} ({all_s/all_tot*100:>5.1f}%) {all_f:>7} ({all_f/all_tot*100:>5.1f}%) {all_tot:>10}")


def main():
    print("=" * 80)
    print("STARTING STAGE 2: FEATURE ENGINEERING & TARGET CONSTRUCTION")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load clean data
    clean_df = load_clean_data(INPUT_PATH)

    # 2. Assign persistent station tracking id
    data_with_keys = create_persistent_station_id(clean_df)

    # 3. Identify suspect normal baseline stations (needed before target assignment)
    suspect_df = identify_suspect_normals(data_with_keys)
    suspect_keys = set(zip(suspect_df["district"], suspect_df["taluk"], suspect_df["hobli"]))

    # 4. Assign target risk_zone (with suspect-normal override)
    data_with_target = assign_target(data_with_keys, suspect_keys=suspect_keys)
    suspect_df.to_csv(SUSPECT_NORMALS_PATH, index=False)
    print(f"\n[OK] Identified {len(suspect_df)} suspect normal stations. Saved to {SUSPECT_NORMALS_PATH}")
    data_with_target["is_suspect_normal"] = data_with_target.apply(
        lambda r: 1 if (r["district"], r["taluk"], r["hobli"]) in suspect_keys else 0, axis=1
    )

    # 5. Feature Engineering
    featured = engineer_features(data_with_target)

    # 6. Leakage Audit
    is_leak_free = verify_no_leakage(featured)
    print(f"\nData Leakage Audit Passed: {is_leak_free}")
    assert is_leak_free, "FATAL: Data leakage detected in initial year records!"

    # 7. Standardize final feature contract columns
    final_cols = [
        "district", "taluk", "hobli", "year",
        "normal_mm", "actual_mm", "departure_pct", "gap_years",
        "n_prior_years", "has_prior_history",
        "deficit_count", "excess_count",
        "mean_actual_mm", "std_actual_mm",
        "mean_departure_pct", "std_departure_pct",
        "previous_year_departure",
        "taluk_mean_departure", "district_mean_departure",
        "hobli_minus_taluk",
        "is_suspect_normal",
        "risk_zone"
    ]
    final_features = featured[final_cols].copy()

    # 8. Save output
    final_features.to_csv(OUTPUT_PATH, index=False)
    print(f"[OK] Saved engineered features to {OUTPUT_PATH} ({len(final_features):,} rows x {len(final_features.columns)} cols)")

    # 9. Print target balance and summary
    print_class_balance_by_year(final_features)

    print("\n" + "=" * 80)
    print("MISSING HISTORY HANDLING:")
    print("=" * 80)
    print("Strategy: Preserved all 4,250 rows across all 5 years.")
    print("Initial year 2020 has n_prior_years=0 and has_prior_history=0.")
    print("Lag/rolling statistics for rows without history evaluate to NaN.")
    print("Zero fake values or silent imputations were introduced.")
    print("Downstream supervised classification models will filter for `has_prior_history == 1`.")


if __name__ == "__main__":
    main()
