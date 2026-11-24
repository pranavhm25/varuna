"""
app/varuna/data.py
==================
Cached data access for the Varuna application. This module only reads the
existing pipeline outputs; it performs no cleaning, no retraining and no
imputation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = ROOT_DIR / "reports"
MODELS_DIR = ROOT_DIR / "models"

CLEAN_PATH = DATA_DIR / "clean" / "clean_rainfall.csv"
FEATURES_PATH = DATA_DIR / "features" / "features.csv"
CLUSTERS_PATH = DATA_DIR / "features" / "hobli_clusters.csv"
FUTURE_PATH = DATA_DIR / "features" / "future_projections_2026_2027.csv"
SUSPECT_PATH = REPORTS_DIR / "suspect_normals.csv"
RESULTS_PATH = MODELS_DIR / "results.csv"

REQUIRED_FILES = [
    CLEAN_PATH,
    FEATURES_PATH,
    CLUSTERS_PATH,
    SUSPECT_PATH,
    RESULTS_PATH,
]


class DataUnavailable(RuntimeError):
    """Raised when a required pipeline artifact is missing or unreadable."""


@dataclass(frozen=True)
class VarunaData:
    clean: pd.DataFrame
    features: pd.DataFrame
    clusters: pd.DataFrame
    suspect: pd.DataFrame
    results: pd.DataFrame
    future: pd.DataFrame
    district_year: pd.DataFrame
    district_pivot: pd.DataFrame
    years: list

    @property
    def suspect_keys(self) -> set:
        return set(zip(self.suspect["district"], self.suspect["taluk"], self.suspect["hobli"]))

    def station_history(self, district: str, taluk: str, hobli: str) -> pd.DataFrame:
        """Observed records for one station, one row per year."""
        sub = self.clean[
            (self.clean["district"] == district)
            & (self.clean["taluk"] == taluk)
            & (self.clean["hobli"] == hobli)
        ].sort_values("year")
        return sub.drop_duplicates(subset=["year"]).reset_index(drop=True)

    def station_cluster(self, district: str, taluk: str, hobli: str) -> pd.Series | None:
        sub = self.clusters[
            (self.clusters["district"] == district)
            & (self.clusters["taluk"] == taluk)
            & (self.clusters["hobli"] == hobli)
        ]
        return sub.iloc[0] if len(sub) else None

    def station_features(self, district: str, taluk: str, hobli: str, year: int) -> pd.Series | None:
        sub = self.features[
            (self.features["district"] == district)
            & (self.features["taluk"] == taluk)
            & (self.features["hobli"] == hobli)
            & (self.features["year"] == year)
        ]
        return sub.iloc[0] if len(sub) else None

    def station_future(self, district: str, taluk: str, hobli: str) -> pd.DataFrame:
        if self.future.empty:
            return self.future
        return self.future[
            (self.future["district"] == district)
            & (self.future["taluk"] == taluk)
            & (self.future["hobli"] == hobli)
        ].sort_values("year")


@st.cache_data(show_spinner=False)
def load_data() -> VarunaData:
    missing = [str(p.relative_to(ROOT_DIR)) for p in REQUIRED_FILES if not p.exists()]
    if missing:
        raise DataUnavailable(
            "Missing required pipeline artifacts: " + ", ".join(missing) +
            ". Run the data preparation and modelling stages first."
        )

    clean = pd.read_csv(CLEAN_PATH)
    features = pd.read_csv(FEATURES_PATH)
    clusters = pd.read_csv(CLUSTERS_PATH)
    suspect = pd.read_csv(SUSPECT_PATH)
    results = pd.read_csv(RESULTS_PATH)
    future = pd.read_csv(FUTURE_PATH) if FUTURE_PATH.exists() else pd.DataFrame()

    district_year = (
        clean.groupby(["district", "year"], as_index=False)
        .agg(departure_pct=("departure_pct", "mean"), stations=("hobli", "size"))
    )
    district_pivot = district_year.pivot(
        index="district", columns="year", values="departure_pct"
    ).sort_index()

    years = sorted(clean["year"].unique().tolist())

    return VarunaData(
        clean=clean,
        features=features,
        clusters=clusters,
        suspect=suspect,
        results=results,
        future=future,
        district_year=district_year,
        district_pivot=district_pivot,
        years=years,
    )


def zone_of(departure: float, drought: float = -20.0, excess: float = 40.0) -> str:
    """Apply the project's fixed KSNDMC risk thresholds to a departure value."""
    if departure <= drought:
        return "drought_prone"
    if departure >= excess:
        return "flood_prone"
    return "stable"


def adjusted_zone_of(
    departure: float,
    normal_mm: float,
    actual_mm: float,
    is_suspect: bool,
    median_normal: float = 700.0,
) -> tuple[str, bool]:
    """Return (zone, was_overridden).

    For suspect-normal stations with very high static normals (> 2 000 mm)
    whose actual rainfall still exceeds the statewide median normal, the
    departure-based "drought_prone" label is an artifact of the benchmark.
    These are overridden to "stable" and the second return value is True.
    """
    raw_zone = zone_of(departure)
    if (
        is_suspect
        and raw_zone == "drought_prone"
        and normal_mm > 2000
        and actual_mm > median_normal
    ):
        return "stable", True
    return raw_zone, False


def zone_series(departures: pd.Series) -> pd.Series:
    return departures.map(zone_of)
