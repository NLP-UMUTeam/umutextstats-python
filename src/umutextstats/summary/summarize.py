from __future__ import annotations

from typing import Any

import pandas as pd

from umutextstats.summary.statistics import (
    DEFAULT_STATISTICS,
    compute_statistics,
)


DEFAULT_EXCLUDE_COLUMNS = {
    "id",
}


def get_numeric_feature_columns(
    df: pd.DataFrame,
    exclude: set[str] | list[str] | tuple[str, ...] | None = None,
) -> list[str]:
    """
    Return numeric feature columns suitable for summary statistics.
    """
    excluded = set(exclude or set()) | DEFAULT_EXCLUDE_COLUMNS

    return [
        column
        for column in df.columns
        if column not in excluded
        and pd.api.types.is_numeric_dtype(df[column])
    ]


def summarize_features( 
    df: pd.DataFrame,
    statistics: tuple[str, ...] | list[str] | None = None,
    exclude: set[str] | list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """
    Compute descriptive statistics for all numeric feature columns.

    Returns a nested dictionary suitable for JSON output.
    """
    selected_statistics = tuple(statistics or DEFAULT_STATISTICS)
    feature_columns = get_numeric_feature_columns(df, exclude=exclude)

    summary: dict[str, dict[str, Any]] = {}

    for column in feature_columns:
        summary[column] = compute_statistics(
            df[column],
            statistics=selected_statistics,
        )

    return {
        "metadata": {
            "documents": int(len(df)),
            "features": int(len(feature_columns)),
            "statistics": list(selected_statistics),
        },
        "summary": summary,
    }


def summarize_features_long(
    df: pd.DataFrame,
    statistics: tuple[str, ...] | list[str] | None = None,
    exclude: set[str] | list[str] | tuple[str, ...] | None = None,
) -> pd.DataFrame:
    """
    Compute descriptive statistics and return a tidy/long DataFrame.

    Recommended for CSV output.
    """
    summary = summarize_features(
        df,
        statistics=statistics,
        exclude=exclude,
    )

    rows: list[dict[str, Any]] = []

    for feature, stats in summary["summary"].items():
        for statistic, value in stats.items():
            rows.append(
                {
                    "feature": feature,
                    "statistic": statistic,
                    "value": value,
                }
            )

    return pd.DataFrame(rows, columns=["feature", "statistic", "value"])