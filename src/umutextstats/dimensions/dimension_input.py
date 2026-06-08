from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DimensionInput:
    """
    Runtime context available to a dimension for a single text/document.
    """

    row: dict[str, Any] = field(default_factory=dict)
    annotations: dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        value = self.row.get("text", "")
        return "" if value is None else str(value)

    @property
    def text_norm(self) -> str:
        value = self.row.get("text_norm", "")
        return "" if value is None else str(value)

    def get(self, key: str, default: Any = None) -> Any:
        return self.row.get(key, default)

    def get_annotation(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.annotations.get(key, default)

    def get_text(
        self,
        input_column: str,
    ) -> str:
        if input_column == "text":
            return self.text

        if input_column == "text_norm":
            return self.text_norm

        value = self.row.get(input_column, "")

        return "" if value is None else str(value)