# src/umutextstats/config/validator.py

from __future__ import annotations

from dataclasses import dataclass

from umutextstats.config.models import DimensionConfig, UMUTextStatsConfig


KNOWN_CLASSES = {
    "CompositeDimension",
    "PatternDimension",
    "WordPerDictionary",
    "VerbPerDictionary",
    "POSTaggingTag",
    "NERTaggingTag",
    "RatioDimension",
    "CharacterCountDimension",
    "LengthDimension",
    "RTIEDimension",
    "RTIEDeviationDimension",
    "WordCountDimension",
    "SyllableCountDimension",
    "SyllablePerWordDimension",
    "WordPerSentenceDimension",
    "WordCase",
    "ReadabilityDimension",
    "PerspicuityDimension",
    "AverageWordLengthDimension",
    "WordLengthDimension",
    "SentenceCountDimension",
    "ErrorCapitalizationStartingWithLowerCaseDimension",
    "ErrorMispellingDimension",
    "ErrorMispellingAccentsDimension",
    "ErrorStyleSentencesStartingWithNumbers",
    "ErrorStyleSentencesStartingWithTheSameWord",
    "ErrorMiscTwoOrMoreEqualWordsDimension",
    "EncliticsPersonalPronounsDictionary",
    "PeriphrasisDimension",
    "TwitterReplyToDimension",
    "DependencyTag",
    "PassiveVoiceDependencyDimension",
    "DependencyDepthDimension",
    "DependencyDistanceDimension",
    "RootPOSTagDimension",
}

KNOWN_STRATEGIES = {
    "CompositeStrategySum",
    "CompositeStrategyAvg",
    "CompositeStrategyMax",
}


@dataclass(frozen=True)
class ConfigValidationIssue:
    level: str
    message: str
    key: str | None = None


class ConfigValidationError(ValueError):
    def __init__(self, issues: list[ConfigValidationIssue]):
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
    result = []

    for dimension in dimensions:
        result.append(dimension)
        result.extend(iter_dimensions(dimension.children))

    return result


def validate_config(config: UMUTextStatsConfig) -> list[ConfigValidationIssue]:
    issues: list[ConfigValidationIssue] = []
    dimensions = iter_dimensions(config.dimensions)

    seen_keys: set[str] = set()

    for dimension in dimensions:
        if not dimension.key:
            issues.append(
                ConfigValidationIssue(
                    level="error",
                    message="Dimension without key.",
                )
            )
            continue

        if dimension.key in seen_keys:
            issues.append(
                ConfigValidationIssue(
                    level="error",
                    key=dimension.key,
                    message="Duplicated dimension key.",
                )
            )

        seen_keys.add(dimension.key)

        if (
            dimension.class_name
            and dimension.class_name not in KNOWN_CLASSES
        ):
            issues.append(
                ConfigValidationIssue(
                    level="error",
                    key=dimension.key,
                    message=f"Unknown class: {dimension.class_name}",
                )
            )

        if (
            dimension.strategy
            and dimension.strategy not in KNOWN_STRATEGIES
        ):
            issues.append(
                ConfigValidationIssue(
                    level="error",
                    key=dimension.key,
                    message=f"Unknown strategy: {dimension.strategy}",
                )
            )

        if dimension.class_name == "RatioDimension":
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

    return issues


def validate_config_or_raise(config: UMUTextStatsConfig) -> None:
    issues = validate_config(config)
    errors = [issue for issue in issues if issue.level == "error"]

    if errors:
        raise ConfigValidationError(errors)