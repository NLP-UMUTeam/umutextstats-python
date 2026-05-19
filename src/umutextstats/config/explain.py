# src/umutextstats/config/explain.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from umutextstats.config.models import DimensionConfig, UMUTextStatsConfig


@dataclass(frozen=True)
class DimensionExplanation:
    dimension: DimensionConfig
    path: list[str]


def find_dimension(
    config: UMUTextStatsConfig,
    key: str,
) -> DimensionExplanation | None:
    for dimension in config.dimensions:
        result = _find_dimension_recursive(
            dimension=dimension,
            key=key,
            path=[],
        )

        if result is not None:
            return result

    return None


def _find_dimension_recursive(
    dimension: DimensionConfig,
    key: str,
    path: list[str],
) -> DimensionExplanation | None:
    current_path = [*path, dimension.key]

    if dimension.key == key:
        return DimensionExplanation(
            dimension=dimension,
            path=current_path,
        )

    for child in dimension.children:
        result = _find_dimension_recursive(
            dimension=child,
            key=key,
            path=current_path,
        )

        if result is not None:
            return result

    return None


def render_dimension_explanation(explanation: DimensionExplanation) -> str:
    data = explanation_to_dict(explanation)

    lines = [
        f"Key: {data['key']}",
        f"Path: {' > '.join(data['path'])}",
    ]

    if data["parent"]:
        lines.append(f"Parent: {data['parent']}")

    if data["class"]:
        lines.append(f"Class: {data['class']}")

    if data["strategy"]:
        lines.append(f"Strategy: {data['strategy']}")

    if data["description"]:
        lines.append(f"Description: {data['description']}")

    lines.append(f"Children count: {data['children_count']}")

    if data["parameters"]:
        lines.append("")
        lines.append("Parameters:")

        for key, value in data["parameters"].items():
            lines.append(f"  {key}: {value}")

    if data["children"]:
        lines.append("")
        lines.append("Children:")

        for child in data["children"]:
            lines.append(f"  - {child}")

    return "\n".join(lines)


def _collect_parameters(dimension: DimensionConfig) -> dict[str, Any]:
    params: dict[str, Any] = {}

    known_values = {
        "dictionary": dimension.dictionary,
        "pattern": dimension.pattern,
        "universal": dimension.universal,
        "use_original_input": dimension.use_original_input,
        "percentage": dimension.percentage,
        "disabled_regexp": dimension.disabled_regexp,
    }

    for key, value in known_values.items():
        if value is None:
            continue

        if key == "use_original_input" and value is False:
            continue

        if key == "percentage" and value is True:
            continue

        if key == "disabled_regexp" and value is False:
            continue

        params[key] = value

    params.update(dimension.params)

    return params


def explanation_to_dict(explanation: DimensionExplanation) -> dict[str, Any]:
    dimension = explanation.dimension
    parent = explanation.path[-2] if len(explanation.path) > 1 else None

    return {
        "key": dimension.key,
        "path": explanation.path,
        "parent": parent,
        "class": dimension.class_name,
        "strategy": dimension.strategy,
        "description": dimension.description,
        "parameters": _collect_parameters(dimension),
        "children_count": len(dimension.children),
        "children": [
            child.key
            for child in dimension.children
        ],
    }