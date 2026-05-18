# src/umutextstats/config/tree.py

from __future__ import annotations

from umutextstats.config.models import DimensionConfig, UMUTextStatsConfig


def render_config_tree(
    config: UMUTextStatsConfig,
    max_depth: int | None = None,
) -> str:
    lines: list[str] = []

    for index, dimension in enumerate(config.dimensions):
        is_last = index == len(config.dimensions) - 1
        _render_dimension(
            dimension=dimension,
            lines=lines,
            prefix="",
            is_last=is_last,
            depth=0,
            max_depth=max_depth,
        )

    return "\n".join(lines)


def _render_dimension(
    dimension: DimensionConfig,
    lines: list[str],
    prefix: str,
    is_last: bool,
    depth: int,
    max_depth: int | None,
) -> None:
    connector = "└── " if is_last else "├── "
    lines.append(f"{prefix}{connector}{dimension.key}")

    if max_depth is not None and depth >= max_depth:
        return

    child_prefix = prefix + ("    " if is_last else "│   ")

    for index, child in enumerate(dimension.children):
        child_is_last = index == len(dimension.children) - 1
        _render_dimension(
            dimension=child,
            lines=lines,
            prefix=child_prefix,
            is_last=child_is_last,
            depth=depth + 1,
            max_depth=max_depth,
        )