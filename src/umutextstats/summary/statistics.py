from __future__ import annotations

from typing import Any

import pandas as pd


DEFAULT_STATISTICS = (
    "count",
    "missing_count",
    "missing_ratio",
    "sum",
    "mean",
    "std",
    "min",
    "q25",
    "median",
    "q75",
    "max",
    "mode",
    "nonzero_count",
    "nonzero_ratio",
)


def compute_statistics(
    series: pd.Series,
    statistics: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    """
    Compute descriptive statistics for a numeric pandas Series.

    Non-numeric values are coerced to NaN and ignored for numeric statistics.
    Missing values are reported separately.
    """
    selected_statistics = tuple(statistics or DEFAULT_STATISTICS)

    original_count = len(series)
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric.dropna()

    result: dict[str, Any] = {}

    if "count" in selected_statistics:
        result["count"] = int(valid.count())

    if "missing_count" in selected_statistics:
        result["missing_count"] = int(original_count - valid.count())

    if "missing_ratio" in selected_statistics:
        result["missing_ratio"] = (
            float((original_count - valid.count()) / original_count)
            if original_count > 0
            else None
        )

    if valid.empty:
        for stat in selected_statistics:
            result.setdefault(stat, None)
        return result

    if "sum" in selected_statistics:
        result["sum"] = float(valid.sum())

    if "mean" in selected_statistics:
        result["mean"] = float(valid.mean())

    if "std" in selected_statistics:
        result["std"] = float(valid.std())

    if "min" in selected_statistics:
        result["min"] = float(valid.min())

    if "q25" in selected_statistics:
        result["q25"] = float(valid.quantile(0.25))

    if "median" in selected_statistics:
        result["median"] = float(valid.median())

    if "q75" in selected_statistics:
        result["q75"] = float(valid.quantile(0.75))

    if "max" in selected_statistics:
        result["max"] = float(valid.max())

    if "mode" in selected_statistics:
        mode = valid.mode()
        result["mode"] = float(mode.iloc[0]) if not mode.empty else None

    if "nonzero_count" in selected_statistics:
        result["nonzero_count"] = int((valid != 0).sum())

    if "nonzero_ratio" in selected_statistics:
        result["nonzero_ratio"] = float((valid != 0).mean())

    return result