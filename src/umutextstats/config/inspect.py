from __future__ import annotations

import regex as re
from rich.console import Group
from rich.text import Text

from umutextstats.io.text import ensure_text
from umutextstats.config.explain import find_dimension
from umutextstats.dimensions.factory import build_runtime_dimension
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.config.models import UMUTextStatsConfig
from umutextstats.inspection.models import (
    InspectMatch,
    DimensionInspection,
)

def _inspect_not_supported_dimension(
    dimension,
    text: str,
) -> DimensionInspection:
    return DimensionInspection(
        key=dimension.key,
        class_name=dimension.class_name,
        pattern=None,
        dictionary=None,
        matches=[],
        discarded_matches=[],
        debug_text=f"Inspection not implemented for {dimension.class_name}",
    )



def inspect_dimension_text(
    config: UMUTextStatsConfig,
    key: str,
    text: str,
    annotations: dict | None = None,
) -> DimensionInspection:
    text = ensure_text(text)

    explanation = find_dimension(config, key)

    if explanation is None:
        raise ValueError(f"Dimension not found: {key}")

    dimension = explanation.dimension
    runtime_dimension = build_runtime_dimension(dimension)

    row = {
        "text": text,
        "text_raw": text,
        "text_norm": text,
    }

    if annotations:
        row.update(annotations)


    item = DimensionInput(
        row=row,
        annotations=annotations or {},
    )

    if runtime_dimension is not None:
        inspection = runtime_dimension.inspect(item)
        if inspection is not None:
            return inspection    


    return _inspect_not_supported_dimension(dimension, text)



def render_inspection(
    inspection: DimensionInspection,
    text: str,
):
    lines = [
        Text(f"Key: {inspection.key}", style="bold"),
    ]

    if inspection.class_name:
        lines.append(Text(f"Class: {inspection.class_name}"))

    if inspection.pattern:
        lines.append(Text(f"Pattern: {inspection.pattern}"))

    if inspection.dictionary:
        lines.append(Text(f"Dictionary: {inspection.dictionary}"))

    lines.append(Text(""))
    lines.append(Text(f"Matches: {len(inspection.matches)}"))

    for match in inspection.matches:
        lines.append(
            Text(f"  - {match.match} [{match.start}:{match.end}]")
        )

    discarded_matches = inspection.discarded_matches or []

    if discarded_matches:
        lines.append(Text(""))
        lines.append(
            Text(
                f"Discarded by exceptions: "
                f"{len(discarded_matches)}"
            )
        )

        for match in discarded_matches:
            lines.append(
                Text(
                    f"  - {match.match} "
                    f"[{match.start}:{match.end}]"
                )
            )

    if inspection.debug_text:
        lines.append(Text(""))
        lines.append(Text("Internal representation:", style="bold"))
        lines.append(Text(inspection.debug_text))

    if inspection.matches:
        lines.append(Text(""))
        lines.append(Text("Highlighted:", style="bold"))
        lines.append(highlight_matches(text, inspection.matches))

    return Group(*lines)


def highlight_matches(text: str, matches: list[InspectMatch]) -> Text:
    highlighted = Text(text)

    for match in matches:
        highlighted.stylize(
            "bold red",
            match.start,
            match.end,
        )

    return highlighted

