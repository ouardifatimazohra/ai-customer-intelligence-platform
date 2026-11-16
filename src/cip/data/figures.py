"""Figures de profilage pour le rapport (RS-001).

Conventions (guide dataviz du projet) : une seule teinte pour une seule série,
marques fines, grille et axes discrets, étiquettes directes en encre de texte
(jamais dans la couleur de la série), pas de double axe.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # rendu sans écran (CI, serveur)

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SERIES = "#2a78d6"  # bleu, validé (contraste >= 3:1 sur la surface claire)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e6e5e1"


def _style(ax: plt.Axes) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=INK_SECONDARY, labelsize=10, length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def churn_distribution(df: pd.DataFrame, out: Path) -> Path:
    """Barres horizontales : nombre de clients par valeur de la cible, étiquetées."""
    counts = df["Churn"].value_counts().reindex(["No", "Yes"])
    labels = {"No": "Restés (No)", "Yes": "Partis (Yes)"}
    total = int(counts.sum())

    fig, ax = plt.subplots(figsize=(7, 2.6), dpi=200, facecolor=SURFACE)
    _style(ax)
    y = range(len(counts))
    ax.barh(list(y), counts.to_numpy(), height=0.55, color=SERIES)
    ax.set_yticks(list(y), [labels[k] for k in counts.index], color=INK, fontsize=11)
    ax.invert_yaxis()
    for i, value in enumerate(counts.to_numpy()):
        ax.text(
            value + total * 0.01,
            i,
            f"{value:,}".replace(",", " ")
            + f"  ({value / total:.1%})".replace(".", ",").replace("%", " %"),
            va="center",
            color=INK,
            fontsize=10,
        )
    ax.set_xlim(0, counts.max() * 1.3)
    ax.set_xlabel("Nombre de clients", color=INK_SECONDARY, fontsize=10)
    ax.set_title(
        f"Répartition de la cible Churn (n = {total:,})".replace(",", " "),
        loc="left",
        color=INK,
        fontsize=12,
        fontweight="bold",
    )
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor=SURFACE)
    plt.close(fig)
    return out


def numeric_distributions(df: pd.DataFrame, out: Path) -> Path:
    """Petits multiples : histogramme de chaque variable numérique, axes indépendants."""
    specs = [
        ("tenure", "Ancienneté (mois)"),
        ("MonthlyCharges", "Charges mensuelles"),
        ("TotalCharges", "Charges totales"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2), dpi=200, facecolor=SURFACE)
    for ax, (col, label) in zip(axes, specs, strict=True):
        values = pd.to_numeric(df[col].str.strip().replace("", None), errors="coerce").dropna()
        _style(ax)
        ax.grid(axis="x", visible=False)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.hist(values, bins=30, color=SERIES, edgecolor=SURFACE, linewidth=1)
        ax.set_title(label, loc="left", color=INK, fontsize=11)
        ax.set_xlabel(f"n = {len(values):,}".replace(",", " "), color=MUTED, fontsize=9)
    axes[0].set_ylabel("Nombre de clients", color=INK_SECONDARY, fontsize=10)
    fig.suptitle(
        "Distribution des variables numériques (valeurs vides exclues)",
        x=0.01,
        ha="left",
        color=INK,
        fontsize=12,
        fontweight="bold",
    )
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor=SURFACE)
    plt.close(fig)
    return out
