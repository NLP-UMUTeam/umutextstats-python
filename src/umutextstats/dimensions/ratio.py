# tests/test_ratio_dimension.py

import pandas as pd

from umutextstats.dimensions.ratio import RatioDimension


def test_ratio_dimension_basic_ratio():
    data = {
        "nouns": pd.Series([2, 4, 0]),
        "verbs": pd.Series([1, 2, 0]),
    }

    dimension = RatioDimension(
        key="noun-to-verb",
        numerator=["nouns"],
        denominator=["verbs"],
    )

    result = dimension.compute_from_data(data, n_rows=3)

    assert list(result) == [2.0, 2.0, 0.0]


def test_ratio_dimension_sums_multiple_numerators_and_denominators():
    data = {
        "nouns": pd.Series([2, 4]),
        "adjectives": pd.Series([3, 1]),
        "verbs": pd.Series([1, 2]),
        "adverbs": pd.Series([1, 2]),
    }

    dimension = RatioDimension(
        key="nominal-to-verbal",
        numerator=["nouns", "adjectives"],
        denominator=["verbs", "adverbs"],
    )

    result = dimension.compute_from_data(data, n_rows=2)

    assert list(result) == [2.5, 1.25]


def test_ratio_dimension_applies_scale():
    data = {
        "a": pd.Series([1, 2]),
        "b": pd.Series([2, 4]),
    }

    dimension = RatioDimension(
        key="scaled-ratio",
        numerator=["a"],
        denominator=["b"],
        scale=100.0,
    )

    result = dimension.compute_from_data(data, n_rows=2)

    assert list(result) == [50.0, 50.0]


def test_ratio_dimension_uses_zero_division_value():
    data = {
        "a": pd.Series([1, 2]),
        "b": pd.Series([0, 0]),
    }

    dimension = RatioDimension(
        key="safe-ratio",
        numerator=["a"],
        denominator=["b"],
        zero_division=-1.0,
    )

    result = dimension.compute_from_data(data, n_rows=2)

    assert list(result) == [-1.0, -1.0]


def test_ratio_dimension_missing_keys_are_treated_as_zero():
    data = {
        "a": pd.Series([1, 2]),
        "b": pd.Series([1, 2]),
    }

    dimension = RatioDimension(
        key="missing-ratio",
        numerator=["a", "missing_num"],
        denominator=["b", "missing_den"],
    )

    result = dimension.compute_from_data(data, n_rows=2)

    assert list(result) == [1.0, 1.0]


def test_ratio_dimension_no_denominator_returns_zero_division():
    data = {
        "a": pd.Series([1, 2]),
    }

    dimension = RatioDimension(
        key="no-denominator",
        numerator=["a"],
        denominator=[],
        zero_division=0.0,
    )

    result = dimension.compute_from_data(data, n_rows=2)

    assert list(result) == [0.0, 0.0]