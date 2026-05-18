# tests/test_config_validator.py

import pytest

from umutextstats.config.models import DimensionConfig, UMUTextStatsConfig
from umutextstats.config.validator import (
    ConfigValidationError,
    validate_config,
    validate_config_or_raise,
)


def test_validate_valid_config():
    config = UMUTextStatsConfig(
        directory_folder="es",
        dimensions=[
            DimensionConfig(
                key="phonetics",
                class_name="CompositeDimension",
                strategy="CompositeStrategySum",
            )
        ],
    )

    assert validate_config(config) == []


def test_validate_duplicated_keys():
    config = UMUTextStatsConfig(
        dimensions=[
            DimensionConfig(key="duplicated"),
            DimensionConfig(key="duplicated"),
        ],
    )

    issues = validate_config(config)

    assert len(issues) == 1
    assert issues[0].key == "duplicated"
    assert "Duplicated" in issues[0].message


def test_validate_unknown_class():
    config = UMUTextStatsConfig(
        dimensions=[
            DimensionConfig(
                key="x",
                class_name="UnknownDimension",
            )
        ],
    )

    issues = validate_config(config)

    assert len(issues) == 1
    assert "Unknown class" in issues[0].message


def test_validate_ratio_requires_numerator_and_denominator():
    config = UMUTextStatsConfig(
        dimensions=[
            DimensionConfig(
                key="ratio",
                class_name="RatioDimension",
            )
        ],
    )

    issues = validate_config(config)

    assert len(issues) == 2
    assert any("numerator" in issue.message for issue in issues)
    assert any("denominator" in issue.message for issue in issues)


def test_validate_config_or_raise():
    config = UMUTextStatsConfig(
        dimensions=[
            DimensionConfig(
                key="x",
                class_name="UnknownDimension",
            )
        ],
    )

    with pytest.raises(ConfigValidationError):
        validate_config_or_raise(config)