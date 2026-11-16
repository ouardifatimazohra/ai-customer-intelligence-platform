"""Tests du profilage (RS-001) sur un petit jeu construit à la main."""

import pandas as pd

from cip.data.figures import churn_distribution, numeric_distributions
from cip.data.profiling import profile


def _sample() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customerID": ["A", "B", "C", "D"],
            "SeniorCitizen": ["0", "1", "0", "0"],
            "Contract": ["Month-to-month", "One year", "Month-to-month", "Two year"],
            "tenure": ["0", "12", "24", "1"],
            "MonthlyCharges": ["20.5", "70", "99.9", "30"],
            "TotalCharges": [" ", "840", "2397.6", "30"],
            "Churn": ["No", "Yes", "No", "No"],
        }
    )


def test_counts_and_target():
    p = profile(_sample())
    assert (p["rows"], p["columns"]) == (4, 7)
    assert p["duplicate_ids"] == 0
    assert p["target"] == {"counts": {"No": 3, "Yes": 1}, "churn_rate": 0.25}


def test_blank_total_charges_linked_to_tenure_zero():
    p = profile(_sample())
    detail = p["columns_detail"]["TotalCharges"]
    assert detail["kind"] == "numeric"
    assert detail["blank_values"] == 1
    assert detail["non_numeric_values"] == 0
    assert p["total_charges_blank_tenures"] == ["0"]
    assert p["tenure_zero_count"] == 1


def test_column_kinds_and_modalities():
    detail = profile(_sample())["columns_detail"]
    assert detail["customerID"]["kind"] == "categorical"  # 4 valeurs distinctes ≤ seuil
    assert detail["Contract"]["modalities"] == {"Month-to-month": 2, "One year": 1, "Two year": 1}
    assert detail["SeniorCitizen"]["modalities"] == {"0": 3, "1": 1}
    assert detail["MonthlyCharges"]["min"] == 20.5


def test_figures_are_written(tmp_path):
    df = _sample()
    a = churn_distribution(df, tmp_path / "a.png")
    b = numeric_distributions(df, tmp_path / "b.png")
    assert a.stat().st_size > 1000
    assert b.stat().st_size > 1000


def test_consistency_rules_detect_violation():
    df = _sample()
    assert profile(df)["consistency"]["blank_total_charges_iff_tenure_zero"] is True
    df.loc[1, "tenure"] = "0"  # tenure 0 mais charges totales renseignées
    assert profile(df)["consistency"]["blank_total_charges_iff_tenure_zero"] is False
