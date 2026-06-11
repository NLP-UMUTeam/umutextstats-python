import pandas as pd

from umutextstats.config.params import param
from umutextstats.inspection.iterable_inspectable_dimension import (
    IterableInspectableDimension,
)
from umutextstats.text.pos import (
    POSItem,
    parse_tagged_pos,
    parse_tagged_pos_with_offsets,
    pos_item_matches,
)


class POSTaggingTag(IterableInspectableDimension):
    """
    Compute the percentage of POS-tagged items matching a configured
    POS tag or universal feature filter.
    """

    def __init__(
        self,
        key: str,
        input_column: str = "tagged_pos",
        postagger_tag: str | None = None,
        postagger_universal: str | None = None,
    ):
        super().__init__(key=key, input_column=input_column)
        self.postagger_tag = postagger_tag
        self.postagger_universal = postagger_universal

    @classmethod
    def from_config(
        cls,
        dimension,
        input_column: str = "tagged_pos",
    ):
        """
        Build the dimension from configuration.
        """
        return cls(
            key=dimension.key,
            input_column=input_column,
            postagger_tag=param(dimension, "tag"),
            postagger_universal=param(dimension, "universal"),
        )

    def compute_single(
        self,
        row: pd.Series,
    ) -> float:
        """
        Compute the matching POS percentage for a single row.
        """
        return self._compute_text(
            self.get_text(row)
        )

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.Series:
        """
        Compute the matching POS percentage for all rows.
        """
        return self.get_text_series(df).apply(
            self._compute_text
        )

    def _compute_text(
        self,
        tagged_text: str,
    ) -> float:
        """
        Compute the percentage of POS items matching the configured filters.
        """
        items = parse_tagged_pos(tagged_text)

        if not items:
            return 0.0

        matches = sum(
            1
            for item in items
            if self._matches(item)
        )

        return (100 * matches) / len(items)

    def iter_matches(
        self,
        tagged_text: str,
    ):
        """
        Yield POS matches for inspection.
        """
        for item in parse_tagged_pos_with_offsets(tagged_text):
            if self._matches(item):
                yield _POSMatch(item)

    def _matches(
        self,
        item: POSItem,
    ) -> bool:
        """
        Check whether a POS item matches the configured filters.
        """
        return pos_item_matches(
            item=item,
            tag=self.postagger_tag,
            universal=self.postagger_universal,
        )

    def inspection_debug_text(self) -> str:
        """
        Return configuration details used during inspection.
        """
        parts = []

        if self.postagger_tag:
            parts.append(f"POS tag: {self.postagger_tag}")

        if self.postagger_universal:
            parts.append(f"Universal features: {self.postagger_universal}")

        return "\n".join(parts) or "No POS filter configured"


class _POSMatch:
    """
    Regex-like wrapper around a POSItem for inspection rendering.
    """

    def __init__(
        self,
        item: POSItem,
    ):
        self.item = item

    def group(
        self,
        index=0,
    ):
        if index != 0:
            raise IndexError(index)

        return self.item.word

    def start(self):
        return self.item.start or 0

    def end(self):
        return self.item.end or 0