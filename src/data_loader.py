from __future__ import annotations
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_tables() -> dict[str, pd.DataFrame]:
    patients = pd.read_csv(DATA_DIR / "patients.csv", parse_dates=["dob"])
    encounters = pd.read_csv(DATA_DIR / "encounters.csv", parse_dates=["date"])
    labs = pd.read_csv(DATA_DIR / "labs.csv", parse_dates=["date"])

    return {
        "patients": patients,
        "encounters": encounters,
        "labs": labs,
    }
