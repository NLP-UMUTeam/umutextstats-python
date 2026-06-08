from __future__ import annotations

from umutextstats.dimensions.base import BaseDimension
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.inspection.models import DimensionInspection


class ScalarInspectableDimension(BaseDimension):
    """
    Base class for dimensions whose inspection is simply
    the scalar value returned by compute_single().
    """

    def inspect(
        self,
        item: DimensionInput,
    ) -> DimensionInspection:
        value = self.compute_single(item)

        return DimensionInspection(
            key=self.key,
            class_name=self.__class__.__name__,
            pattern=None,
            dictionary=None,
            matches=[],
            discarded_matches=[],
            debug_text=f"Value: {value}",
        )