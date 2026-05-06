from __future__ import annotations

from typing import Any

import pandas as pd

from umutextstats.summary.summarize import (
    summarize_features,
)


def aggregate_features(
    df: pd.DataFrame,
    group_by: str,
    statistics=None,
    exclude=None,
) -> dict[str, Any]:
    """
    Compute grouped summary statistics.

    Parameters
    ----------
    df:
        Input DataFrame containing features and grouping columns.

    group_by:
        Column name used for grouping.

    statistics:
        Optional list of statistics to compute.

    exclude:
        Optional columns to exclude from summary.
    """
    if group_by not in df.columns:
        raise ValueError(
            f"Group column '{group_by}' not found in DataFrame."
        )

    groups: dict[str, Any] = {}

    for value, subset in df.groupby(group_by):
        groups[str(value)] = summarize_features(
            subset,
            statistics=statistics,
            exclude=exclude,
        )

    return {
        "group_by": group_by,
        "groups": groups,
    }