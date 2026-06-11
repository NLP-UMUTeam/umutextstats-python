from __future__ import annotations

from typing import Iterable

import pandas as pd

from umutextstats.dimensions.base import BaseDimension
from umutextstats.inspection.models import (
    DimensionInspection,
    InspectMatch,
)


class IterableInspectableDimension(BaseDimension):
    """
    Base class for dimensions explainable through regex-like matches.

    Subclasses must implement `iter_matches(text)`.
    They may optionally implement `iter_discarded_matches(text)`.
    """

    pattern: str | None = None
    dictionary: str | None = None

    def inspect(
        self,
        row: pd.Series,
    ) -> DimensionInspection:
        """
        Build an inspection object for a single DataFrame row.
        """
        text = self.get_text(row)

        value = self.compute_single(row)

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
            pattern=self.pattern,
            dictionary=self.dictionary,
            matches=matches,
            discarded_matches=discarded_matches,
            debug_text=self._build_debug_text(value),
        )

    def iter_matches(
        self,
        text: str,
    ) -> Iterable:
        """
        Yield matches contributing to the dimension value.
        """
        return []

    def iter_discarded_matches(
        self,
        text: str,
    ) -> Iterable:
        """
        Yield matches that were detected but discarded.
        """
        return []

    def inspection_debug_text(
        self,
    ) -> str | None:
        """
        Return additional debug information shown during inspection.
        """
        if self.pattern:
            return self.pattern

        if self.dictionary:
            return f"Loaded dictionary: {self.dictionary}"

        return None

    def _to_inspect_match(
        self,
        match,
    ) -> InspectMatch:
        """
        Convert a regex-like match object into an InspectMatch.
        """
        return InspectMatch(
            match=match.group(0),
            start=match.start(),
            end=match.end(),
        )

    def _build_debug_text(
        self,
        value=None,
    ) -> str | None:
        """
        Build the inspection debug text shown below matches.
        """
        lines = []

        if value is not None:
            lines.append(f"Value: {value}")

        if self.pattern:
            lines.append(str(self.pattern))

        if self.dictionary:
            lines.append(
                f"Loaded dictionary: {self.dictionary}"
            )

        return "\n".join(lines) if lines else None