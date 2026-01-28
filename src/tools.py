from __future__ import annotations
import pandas as pd

def list_tables(tables: dict[str, pd.DataFrame]) -> str:
    return "Available tables: " + ", ".join(sorted(tables.keys()))

def show_schema(tables: dict[str, pd.DataFrame]) -> str:
    lines = []
    for name, df in tables.items():
        lines.append(f"{name}: {', '.join(df.columns)}")
    return "\n".join(lines)

def find_patient(tables: dict[str, pd.DataFrame], name_contains: str) -> str:
    df = tables["patients"]
    m = df["name"].str.contains(name_contains, case=False, na=False)
    out = df.loc[m, ["patient_id", "name", "sex", "dob"]].copy()
    if out.empty:
        return f"No patients found matching '{name_contains}'."
    return out.to_string(index=False)

def patients_by_icd10(tables: dict[str, pd.DataFrame], icd10: str) -> str:
    enc = tables["encounters"]
    pats = tables["patients"]
    hit = enc[enc["icd10"] == icd10][["patient_id"]].drop_duplicates()
    out = pats.merge(hit, on="patient_id", how="inner")[["patient_id", "name", "sex", "dob"]]
    if out.empty:
        return f"No patients found with ICD-10 '{icd10}'."
    return out.to_string(index=False)

def latest_lab(tables: dict[str, pd.DataFrame], patient_id: str, test: str) -> str:
    labs = tables["labs"]
    sub = labs[(labs["patient_id"] == patient_id) & (labs["test"].str.upper() == test.upper())].copy()
    if sub.empty:
        return f"No lab '{test}' found for {patient_id}."
    sub = sub.sort_values("date", ascending=False).head(1)
    row = sub.iloc[0]
    return f"{patient_id} latest {row['test']} = {row['value']} {row['unit']} on {row['date'].date()}"

def patient_summary(tables: dict[str, pd.DataFrame], patient_id: str) -> str:
    pats = tables["patients"]
    enc = tables["encounters"]
    labs = tables["labs"]

    p = pats[pats["patient_id"] == patient_id]
    if p.empty:
        return f"Unknown patient_id: {patient_id}"
    p = p.iloc[0]

    enc_sub = enc[enc["patient_id"] == patient_id].sort_values("date", ascending=False).head(5)
    labs_sub = labs[labs["patient_id"] == patient_id].sort_values("date", ascending=False).head(5)

    parts = [
        f"Patient: {p['patient_id']} | {p['name']} | {p['sex']} | DOB {p['dob'].date()}",
        "\nRecent encounters (max 5):",
        enc_sub[["date", "visit_type", "icd10"]].to_string(index=False) if not enc_sub.empty else "None",
        "\nRecent labs (max 5):",
        labs_sub[["date", "test", "value", "unit"]].to_string(index=False) if not labs_sub.empty else "None",
    ]
    return "\n".join(parts)
