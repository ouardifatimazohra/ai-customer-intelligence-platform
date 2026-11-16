"""Profilage du dataset source (RS-001).

Toutes les valeurs citées dans la documentation (volumes, valeurs manquantes,
modalités, taux de churn) sont **calculées ici**, jamais saisies à la main.
Le fichier source est lu entièrement en texte (`dtype=str`) pour observer les
données telles qu'elles sont, avant toute conversion.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

NUMERIC_CANDIDATES = ("tenure", "MonthlyCharges", "TotalCharges")
TARGET = "Churn"
ID_COLUMN = "customerID"
MAX_MODALITIES = 12  # au-delà, une colonne texte est considérée comme non catégorielle


def load_raw(path: Path) -> pd.DataFrame:
    """Lit le CSV sans aucune conversion (toutes les colonnes en texte)."""
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")


def _to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.str.strip().replace("", None), errors="coerce")


def profile(df: pd.DataFrame) -> dict[str, Any]:
    """Calcule les faits de profilage du DataFrame brut."""
    columns: dict[str, Any] = {}
    for col in df.columns:
        raw = df[col]
        blank = int((raw.str.strip() == "").sum())
        distinct = int(raw.nunique())
        info: dict[str, Any] = {
            "blank_values": blank,
            "distinct_values": distinct,
            "leading_or_trailing_spaces": int((raw != raw.str.strip()).sum()),
        }
        numeric = _to_number(raw)
        non_numeric = int(numeric.isna().sum()) - blank
        if col in NUMERIC_CANDIDATES or (non_numeric == 0 and distinct > MAX_MODALITIES):
            info["kind"] = "numeric"
            info["non_numeric_values"] = non_numeric
            info["min"] = float(numeric.min())
            info["max"] = float(numeric.max())
            info["mean"] = round(float(numeric.mean()), 4)
            info["median"] = float(numeric.median())
        elif distinct <= MAX_MODALITIES:
            info["kind"] = "categorical"
            info["modalities"] = {k: int(v) for k, v in raw.value_counts().sort_index().items()}
        else:
            info["kind"] = "identifier"
        columns[col] = info

    result: dict[str, Any] = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns_detail": columns,
    }

    if ID_COLUMN in df.columns:
        result["duplicate_ids"] = int(df[ID_COLUMN].duplicated().sum())

    if TARGET in df.columns:
        counts = df[TARGET].value_counts()
        result["target"] = {
            "counts": {k: int(v) for k, v in counts.items()},
            "churn_rate": round(float((df[TARGET] == "Yes").mean()), 4),
        }

    if {"TotalCharges", "tenure"} <= set(df.columns):
        blank_total = df["TotalCharges"].str.strip() == ""
        result["total_charges_blank_tenures"] = sorted(df.loc[blank_total, "tenure"].unique())
        tenure = _to_number(df["tenure"])
        result["tenure_zero_count"] = int((tenure == 0).sum())

    result["consistency"] = _consistency(df)
    return result


INTERNET_DEPENDENT = (
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
)


def _consistency(df: pd.DataFrame) -> dict[str, bool]:
    """Règles de cohérence vérifiées ligne à ligne (True = respectée partout)."""
    checks: dict[str, bool] = {}
    cols = set(df.columns)
    if {"MultipleLines", "PhoneService"} <= cols:
        checks["no_phone_service_iff_phone_service_no"] = bool(
            ((df["MultipleLines"] == "No phone service") == (df["PhoneService"] == "No")).all()
        )
    if {"InternetService", *INTERNET_DEPENDENT} <= cols:
        no_internet = df["InternetService"] == "No"
        checks["no_internet_service_iff_internet_service_no"] = all(
            ((df[c] == "No internet service") == no_internet).all() for c in INTERNET_DEPENDENT
        )
    if {"TotalCharges", "tenure"} <= cols:
        checks["blank_total_charges_iff_tenure_zero"] = bool(
            ((df["TotalCharges"].str.strip() == "") == (df["tenure"].str.strip() == "0")).all()
        )
    if ID_COLUMN in cols:
        checks["customer_id_format_NNNN-XXXXX"] = bool(
            df[ID_COLUMN].str.fullmatch(r"\d{4}-[A-Z]{5}").all()
        )
    return checks


def save_profile(result: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
