# src/umutextstats/config/yaml_exporter.py

from pathlib import Path
from typing import Any

import yaml

from umutextstats.config.models import DimensionConfig, UMUTextStatsConfig


def _clean_dict(data: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if value is not None
        and value != []
        and value != {}
    }


def dimension_to_dict(dimension: DimensionConfig) -> dict[str, Any]:
    data = {
        "key": dimension.key,
        "class": dimension.class_name,
        "strategy": dimension.strategy,
        "description": dimension.description,
        "dictionary": dimension.dictionary,
        "pattern": dimension.pattern,
        "universal": dimension.universal,
        "use_original_input": (
            dimension.use_original_input
            if dimension.use_original_input is not False
            else None
        ),
        "percentage": (
            dimension.percentage
            if dimension.percentage is not True
            else None
        ),
        "disabled_regexp": (
            dimension.disabled_regexp
            if dimension.disabled_regexp is not False
            else None
        ),
        "children": [
            dimension_to_dict(child)
            for child in dimension.children
        ],
    }

    data.update(dimension.params)

    return _clean_dict(data)


def config_to_dict(config: UMUTextStatsConfig) -> dict[str, Any]:
    return _clean_dict(
        {
            "directory_folder": config.directory_folder,
            "dimensions": [
                dimension_to_dict(dimension)
                for dimension in config.dimensions
            ],
        }
    )


def dump_yaml_config(config: UMUTextStatsConfig) -> str:
    return yaml.safe_dump(
        config_to_dict(config),
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )


def save_yaml_config(config: UMUTextStatsConfig, path: str | Path) -> None:
    path = Path(path)
    path.write_text(dump_yaml_config(config), encoding="utf-8")