# src/umutextstats/summary/ranking.py

from __future__ import annotations

from typing import Any

import pandas as pd


def summary_to_long_dataframe(summary: dict[str, Any]) -> pd.DataFrame:
    """
    Convert nested summary dict into a long/tidy DataFrame.

    Expected input:
    {
        "metadata": {...},
        "summary": {
            "feature_a": {"mean": 1.2, "std": 0.3},
            ...
        }
    }
    """
    rows: list[dict[str, Any]] = []

    for feature, statistics in summary.get("summary", {}).items():
        for statistic, value in statistics.items():
            rows.append(
                {
                    "feature": feature,
                    "statistic": statistic,
                    "value": value,
                }
            )

    return pd.DataFrame(rows, columns=["feature", "statistic", "value"])


def rank_features(
    summary: dict[str, Any],
    by: str = "mean",
    top: int | None = 20,
    ascending: bool = False,
) -> pd.DataFrame:
    """
    Rank features by a selected statistic.
    """
    rows: list[dict[str, Any]] = []

    for feature, statistics in summary.get("summary", {}).items():
        if by not in statistics:
            continue

        value = statistics[by]

        if value is None:
            continue

        rows.append(
            {
                "feature": feature,
                "statistic": by,
                "value": value,
            }
        )

    ranking = pd.DataFrame(rows, columns=["feature", "statistic", "value"])

    if ranking.empty:
        return ranking

    ranking = ranking.sort_values(
        by="value",
        ascending=ascending,
    ).reset_index(drop=True)

    ranking.insert(0, "rank", range(1, len(ranking) + 1))

    if top is not None:
        ranking = ranking.head(top)

    return ranking


def get_zero_only_features(
    summary: dict[str, Any],
) -> pd.DataFrame:
    """
    Return features whose nonzero_count is 0.
    """
    rows: list[dict[str, Any]] = []

    for feature, statistics in summary.get("summary", {}).items():
        nonzero_count = statistics.get("nonzero_count")

        if nonzero_count == 0:
            rows.append(
                {
                    "feature": feature,
                    "nonzero_count": nonzero_count,
                    "nonzero_ratio": statistics.get("nonzero_ratio"),
                }
            )

    return pd.DataFrame(
        rows,
        columns=["feature", "nonzero_count", "nonzero_ratio"],
    )


def get_sparse_features(
    summary: dict[str, Any],
    threshold: float = 0.01,
) -> pd.DataFrame:
    """
    Return features with nonzero_ratio <= threshold.
    """
    rows: list[dict[str, Any]] = []

    for feature, statistics in summary.get("summary", {}).items():
        nonzero_ratio = statistics.get("nonzero_ratio")

        if nonzero_ratio is None:
            continue

        if nonzero_ratio <= threshold:
            rows.append(
                {
                    "feature": feature,
                    "nonzero_count": statistics.get("nonzero_count"),
                    "nonzero_ratio": nonzero_ratio,
                }
            )

    sparse = pd.DataFrame(
        rows,
        columns=["feature", "nonzero_count", "nonzero_ratio"],
    )

    if sparse.empty:
        return sparse

    return sparse.sort_values(
        by="nonzero_ratio",
        ascending=True,
    ).reset_index(drop=True)