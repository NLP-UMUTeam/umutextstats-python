# src/umutextstats/config/validator.py

from __future__ import annotations

from dataclasses import dataclass

from umutextstats.config.models import DimensionConfig, UMUTextStatsConfig
from umutextstats.dimensions.registry import resolve_dimension


KNOWN_STRATEGIES = {
    "CompositeStrategySum",
    "CompositeStrategyAvg",
    "CompositeStrategyMax",
}


@dataclass(frozen=True)
class ConfigValidationIssue:
    """
    Validation issue found in a UMUTextStats configuration.
    """

    level: str
    message: str
    key: str | None = None


class ConfigValidationError(ValueError):
    """
    Error raised when configuration validation finds blocking issues.
    """

    def __init__(
        self,
        issues: list[ConfigValidationIssue],
    ):
        self.issues = issues

        message = "\n".join(
            f"[{issue.level}]"
            f"{f' {issue.key}:' if issue.key else ''} "
            f"{issue.message}"
            for issue in issues
        )

        super().__init__(message)


def iter_dimensions(
    dimensions: list[DimensionConfig],
) -> list[DimensionConfig]:
    """
    Flatten a dimension tree into a list.
    """
    result = []

    for dimension in dimensions:
        result.append(dimension)
        result.extend(
            iter_dimensions(dimension.children)
        )

    return result


def validate_config(
    config: UMUTextStatsConfig,
) -> list[ConfigValidationIssue]:
    """
    Validate a UMUTextStats configuration.

    The validator checks structural issues such as duplicated keys,
    unknown dimension classes, unknown composite strategies, and missing
    required parameters for dimensions that need them.
    """
    issues: list[ConfigValidationIssue] = []
    dimensions = iter_dimensions(config.dimensions)

    seen_keys: set[str] = set()
    available_keys = {
        dimension.key
        for dimension in dimensions
        if dimension.key
    }

    for dimension in dimensions:
        _validate_key(
            dimension=dimension,
            seen_keys=seen_keys,
            issues=issues,
        )

        _validate_class(
            dimension=dimension,
            issues=issues,
        )

        _validate_strategy(
            dimension=dimension,
            issues=issues,
        )

        _validate_ratio_dimension(
            dimension=dimension,
            available_keys=available_keys,
            issues=issues,
        )

    return issues


def validate_config_or_raise(
    config: UMUTextStatsConfig,
) -> None:
    """
    Validate a configuration and raise if any error-level issue exists.
    """
    issues = validate_config(config)
    errors = [
        issue
        for issue in issues
        if issue.level == "error"
    ]

    if errors:
        raise ConfigValidationError(errors)


def _validate_key(
    dimension: DimensionConfig,
    seen_keys: set[str],
    issues: list[ConfigValidationIssue],
) -> None:
    """
    Validate dimension key presence and uniqueness.
    """
    if not dimension.key:
        issues.append(
            ConfigValidationIssue(
                level="error",
                message="Dimension without key.",
            )
        )
        return

    if dimension.key in seen_keys:
        issues.append(
            ConfigValidationIssue(
                level="error",
                key=dimension.key,
                message="Duplicated dimension key.",
            )
        )

    seen_keys.add(dimension.key)


def _validate_class(
    dimension: DimensionConfig,
    issues: list[ConfigValidationIssue],
) -> None:
    """
    Validate that the configured dimension class exists in the registry.
    """
    if not dimension.class_name:
        return

    if resolve_dimension(dimension.class_name) is None:
        issues.append(
            ConfigValidationIssue(
                level="error",
                key=dimension.key,
                message=f"Unknown class: {dimension.class_name}",
            )
        )


def _validate_strategy(
    dimension: DimensionConfig,
    issues: list[ConfigValidationIssue],
) -> None:
    """
    Validate composite strategy names.
    """
    if not dimension.strategy:
        return

    if dimension.strategy not in KNOWN_STRATEGIES:
        issues.append(
            ConfigValidationIssue(
                level="error",
                key=dimension.key,
                message=f"Unknown strategy: {dimension.strategy}",
            )
        )


def _validate_ratio_dimension(
    dimension: DimensionConfig,
    available_keys: set[str],
    issues: list[ConfigValidationIssue],
) -> None:
    """
    Validate RatioDimension parameters.

    Ratio dimensions reference previously computed dimension keys through
    numerator and denominator parameters.
    """
    if dimension.class_name != "RatioDimension":
        return

    numerator = dimension.params.get("numerator")
    denominator = dimension.params.get("denominator")

    if not numerator:
        issues.append(
            ConfigValidationIssue(
                level="error",
                key=dimension.key,
                message="RatioDimension without numerator.",
            )
        )

    if not denominator:
        issues.append(
            ConfigValidationIssue(
                level="error",
                key=dimension.key,
                message="RatioDimension without denominator.",
            )
        )

    if numerator:
        _validate_ratio_keys(
            dimension=dimension,
            field="numerator",
            raw_keys=numerator,
            available_keys=available_keys,
            issues=issues,
        )

    if denominator:
        _validate_ratio_keys(
            dimension=dimension,
            field="denominator",
            raw_keys=denominator,
            available_keys=available_keys,
            issues=issues,
        )


def _validate_ratio_keys(
    dimension: DimensionConfig,
    field: str,
    raw_keys,
    available_keys: set[str],
    issues: list[ConfigValidationIssue],
) -> None:
    """
    Validate that RatioDimension referenced keys exist in the config.
    """
    keys = _split_ratio_keys(raw_keys)

    for key in keys:
        if key not in available_keys:
            issues.append(
                ConfigValidationIssue(
                    level="error",
                    key=dimension.key,
                    message=(
                        f"RatioDimension {field} references "
                        f"unknown dimension: {key}"
                    ),
                )
            )


def _split_ratio_keys(raw_keys) -> list[str]:
    """
    Normalize a ratio key list.

    Ratio keys can be configured as a pipe-separated string or as a list.
    """
    if isinstance(raw_keys, list):
        return [
            str(key).strip()
            for key in raw_keys
            if str(key).strip()
        ]

    return [
        key.strip()
        for key in str(raw_keys).split("|")
        if key.strip()
    ]