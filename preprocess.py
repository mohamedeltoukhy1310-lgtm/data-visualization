"""
Data pipeline: read raw Our World in Data–style CSV, clean, derive metrics,
and write all files expected by the Dash app.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW = DATA / "owid-covid-data.csv"

OUT_CLEANED = DATA / "cleaned_data.csv"
OUT_SCATTER = DATA / "scatter.csv"
OUT_BUBBLE = DATA / "bubble.csv"
OUT_HIST = DATA / "hist_data.csv"
OUT_BOX = DATA / "box_data.csv"

# Non-country rows when iso_code is absent (name-based fallback)
EXCLUDE_LOCATIONS = {
    "World",
    "International",
    "European Union",
    "High income",
    "Upper middle income",
    "Lower middle income",
    "Low income",
    "Asia",
    "Europe",
    "Africa",
    "North America",
    "South America",
    "Oceania",
}

NUMERIC_BASE = [
    "population",
    "total_cases",
    "new_cases",
    "total_deaths",
    "new_deaths",
    "total_vaccinations",
    "people_vaccinated",
    "gdp_per_capita",
    "population_density",
]

FINAL_COLS = [
    "date",
    "location",
    "continent",
    "population",
    "total_cases",
    "new_cases",
    "total_deaths",
    "new_deaths",
    "total_vaccinations",
    "people_vaccinated",
    "gdp_per_capita",
    "population_density",
    "death_rate",
    "vaccination_rate",
    "cases_per_million",
]

# Minimum wide-OWID fields to build the master table if 15-col snapshot is not used
WIDE_REQUIRED = {
    "date",
    "location",
    "population",
    "total_cases",
    "new_deaths",
    "total_deaths",
    "new_cases",
}


def load_raw() -> pd.DataFrame:
    if not RAW.exists():
        raise FileNotFoundError(
            f"Place the dataset at {RAW} (e.g. owid-covid-data.csv from Our World in Data)."
        )
    return pd.read_csv(RAW, low_memory=False)


def report_schema(df: pd.DataFrame) -> None:
    n = len(df.columns)
    print(f"  Columns: {n} (full OWID export is often ~60+; your project table uses 15).")
    print(f"  First columns: {list(df.columns)[:12]}{' ...' if n > 12 else ''}")


def filter_country_rows(df: pd.DataFrame) -> pd.DataFrame:
    if "iso_code" in df.columns:
        iso = df["iso_code"].astype(str)
        mask = iso.str.match(r"^[A-Z]{3}$", na=False)
        return df.loc[mask].copy()
    if "location" not in df.columns:
        raise ValueError("Expected a 'location' column.")
    loc = df["location"].astype(str)
    return df.loc[~loc.isin(EXCLUDE_LOCATIONS)].copy()


def _from_wide_owid(df: pd.DataFrame) -> pd.DataFrame:
    missing = WIDE_REQUIRED - set(df.columns)
    if missing:
        raise ValueError(
            f"Raw file is missing required columns: {sorted(missing)}. "
            "Use the full Our World in Data dataset or the 15-column project schema."
        )
    out = pd.DataFrame(
        {
            "date": df["date"],
            "location": df["location"],
            "continent": df["continent"] if "continent" in df.columns else np.nan,
            "population": df["population"],
            "total_cases": df["total_cases"],
            "new_cases": df["new_cases"],
            "total_deaths": df["total_deaths"],
            "new_deaths": df["new_deaths"],
            "total_vaccinations": df.get("total_vaccinations", 0.0),
            "people_vaccinated": df.get("people_vaccinated", 0.0),
            "gdp_per_capita": df.get("gdp_per_capita", 0.0),
            "population_density": df.get("population_density", 0.0),
        }
    )
    if "continent" in out.columns:
        out["continent"] = out["continent"].fillna("Unknown")
    return out


def _finalize_metrics(out: pd.DataFrame) -> pd.DataFrame:
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    for c in NUMERIC_BASE:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)

    pop = out["population"].replace(0, np.nan)
    cases = pd.to_numeric(out["total_cases"], errors="coerce").fillna(0.0)
    deaths = pd.to_numeric(out["total_deaths"], errors="coerce").fillna(0.0)
    vacc = pd.to_numeric(out["people_vaccinated"], errors="coerce").fillna(0.0)

    out["death_rate"] = np.where(cases > 0, (deaths / cases) * 100.0, 0.0)
    out["vaccination_rate"] = np.where(
        pop.notna() & (pop > 0), (vacc / pop) * 100.0, 0.0
    )
    out["cases_per_million"] = np.where(
        pop.notna() & (pop > 0), (cases / pop) * 1_000_000.0, 0.0
    )

    out = out.dropna(subset=["date"])
    return out[FINAL_COLS]


def build_master(df: pd.DataFrame) -> pd.DataFrame:
    if set(FINAL_COLS).issubset(df.columns):
        base = df[list(FINAL_COLS)].copy()
        return _finalize_metrics(base)
    base = _from_wide_owid(df)
    return _finalize_metrics(base)


def write_derived(master: pd.DataFrame) -> None:
    master.sort_values(["location", "date"]).to_csv(OUT_CLEANED, index=False)

    master[["date", "gdp_per_capita", "total_cases", "continent"]].to_csv(
        OUT_SCATTER, index=False
    )
    master[
        ["date", "population_density", "total_cases", "population", "continent"]
    ].to_csv(OUT_BUBBLE, index=False)
    master[["location", "death_rate"]].to_csv(OUT_HIST, index=False)
    master[["continent", "vaccination_rate", "cases_per_million"]].to_csv(
        OUT_BOX, index=False
    )


def main() -> None:
    print(f"Reading {RAW} ...")
    df = load_raw()
    print(f"  Rows: {len(df):,}")
    report_schema(df)

    filtered = filter_country_rows(df)
    print(f"After excluding aggregates / non-country rows: {len(filtered):,} rows.")

    master = build_master(filtered)
    write_derived(master)
    print("Written:")
    for p in (OUT_CLEANED, OUT_SCATTER, OUT_BUBBLE, OUT_HIST, OUT_BOX):
        print(f"  {p}")


if __name__ == "__main__":
    main()
