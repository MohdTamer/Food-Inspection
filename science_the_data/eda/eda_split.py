from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger

TARGET_COL = "Results"
DATE_COL   = "Inspection Date"


def compute_eda_stats(
    df: pd.DataFrame,
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    cutoff_date: pd.Timestamp,
    figures_dir: Path,
) -> dict:
    figures_dir.mkdir(parents=True, exist_ok=True)

    eda: dict = {}

    eda["split_summary"] = [
        {
            "split":      "Train",
            "rows":       len(df_train),
            "pct":        f"{len(df_train) / len(df) * 100:.1f}%",
            "date_start": df_train[DATE_COL].min().date(),
            "date_end":   df_train[DATE_COL].max().date(),
        },
        {
            "split":      "Test",
            "rows":       len(df_test),
            "pct":        f"{len(df_test) / len(df) * 100:.1f}%",
            "date_start": df_test[DATE_COL].min().date(),
            "date_end":   df_test[DATE_COL].max().date(),
        },
        {
            "split":      "Overall",
            "rows":       len(df),
            "pct":        "100.0%",
            "date_start": df[DATE_COL].min().date(),
            "date_end":   df[DATE_COL].max().date(),
        },
    ]

    eda["date_range"] = {
        "min":        str(df[DATE_COL].min().date()),
        "max":        str(df[DATE_COL].max().date()),
        "total_days": (df[DATE_COL].max() - df[DATE_COL].min()).days,
    }
    eda["cutoff_date"] = str(cutoff_date.date())

    class_labels = sorted(df[TARGET_COL].dropna().unique().tolist())
    eda["class_labels"] = class_labels

    eda["target_dist"] = {}
    for label, subset in [("Train", df_train), ("Test", df_test), ("Overall", df)]:
        counts = subset[TARGET_COL].value_counts()
        pcts   = subset[TARGET_COL].value_counts(normalize=True).mul(100)
        eda["target_dist"][label] = {
            cls: {
                "count": int(counts.get(cls, 0)),
                "pct":   float(pcts.get(cls, 0.0)),
            }
            for cls in class_labels
        }

    eda["figures"] = {
        "target_distribution":   _fig_target_distribution(df, df_train, df_test, figures_dir),
        "inspections_over_time": _fig_inspections_over_time(df_train, df_test, figures_dir),
    }

    return eda

def _fig_target_distribution(
    df: pd.DataFrame,
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    figures_dir: Path,
) -> Path:
    bar_colors = ["#2ecc71", "#e74c3c", "#f39c12", "#3498db", "#9b59b6"]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)

    for ax, (subset, title) in zip(
        axes,
        [(df_train, "Train"), (df_test, "Test"), (df, "Overall")],
    ):
        pcts = subset[TARGET_COL].value_counts(normalize=True).mul(100).sort_index()
        pcts.plot.bar(ax=ax, color=bar_colors[: len(pcts)], edgecolor="white") # type: ignore
        ax.set_title(title, fontweight="bold")
        ax.set_ylabel("Percentage (%)" if ax is axes[0] else "")
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=30)
        for bar in ax.patches:
            ax.annotate(
                f"{bar.get_height():.1f}%",
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                ha="center", va="bottom", fontsize=9,
            )

    fig.suptitle(
        "Target (Results) Distribution by Split",
        fontsize=13, fontweight="bold", y=1.02,
    )
    plt.tight_layout()

    out = figures_dir / "target_distribution_by_split.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved figure → {}", out)
    return out


def _fig_inspections_over_time(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    figures_dir: Path,
) -> Path:
    train_monthly = df_train.set_index(DATE_COL).resample("ME").size().rename("Train")
    test_monthly  = df_test.set_index(DATE_COL).resample("ME").size().rename("Test")

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.fill_between(train_monthly.index, train_monthly, alpha=0.4, color="#3498db", label="Train")
    ax.fill_between(test_monthly.index,  test_monthly,  alpha=0.4, color="#e74c3c", label="Test")
    ax.plot(train_monthly.index, train_monthly, color="#3498db", linewidth=1.5)
    ax.plot(test_monthly.index,  test_monthly,  color="#e74c3c", linewidth=1.5)
    ax.set_title("Monthly Inspection Volume by Split", fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Inspections")
    ax.legend()
    plt.tight_layout()

    out = figures_dir / "inspections_over_time.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved figure → {}", out)
    return out