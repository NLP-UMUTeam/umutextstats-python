from __future__ import annotations

from typing import Iterable

from umutextstats.dimensions.base import BaseDimension
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.models import DimensionInspection, InspectMatch


class IterableInspectableDimension(BaseDimension):
    """
    Base class for dimensions explainable through regex-like matches.

    Subclasses must implement iter_matches(text).
    They may optionally implement iter_discarded_matches(text).
    """

    pattern: str | None = None
    dictionary: str | None = None

    def inspect(
        self,
        item: DimensionInput,
    ) -> DimensionInspection:
        text = self.get_text(item)

        value = (
            self.compute_single(item)
            if hasattr(self, "compute_single")
            else None
        )

        matches = [
            self._to_inspect_match(match)
            for match in self.iter_matches(text)
        ]

        discarded_matches = [
            self._to_inspect_match(match)
            for match in self.iter_discarded_matches(text)
        ]

        return DimensionInspection(
            key=self.key,
            class_name=self.__class__.__name__,
            pattern=getattr(self, "pattern", None),
            dictionary=getattr(self, "dictionary", None),
            matches=matches,
            discarded_matches=discarded_matches,
            debug_text=self._build_debug_text(value),
        )

    def iter_matches(self, text: str) -> Iterable:
        return []

    def iter_discarded_matches(self, text: str) -> Iterable:
        return []

    def inspection_debug_text(self) -> str | None:
        pattern = getattr(self, "pattern", None)

        if pattern:
            return pattern

        dictionary = getattr(self, "dictionary", None)

        if dictionary:
            return f"Loaded dictionary: {dictionary}"

        return None

    def _to_inspect_match(self, match) -> InspectMatch:
        return InspectMatch(
            match=match.group(0),
            start=match.start(),
            end=match.end(),
        )
    
    def _build_debug_text(
        self,
        value=None,
    ) -> str | None:
        lines = []

        if value is not None:
            lines.append(f"Value: {value}")

        pattern = getattr(self, "pattern", None)

        if pattern:
            lines.append(str(pattern))

        dictionary = getattr(self, "dictionary", None)

        if dictionary:
            lines.append(
                f"Loaded dictionary: {dictionary}"
            )

        return "\n".join(lines) if lines else None