from __future__ import annotations

import pandas as pd

from umutextstats.dimensions.base import BaseDimension
from umutextstats.inspection.models import DimensionInspection


class ScalarInspectableDimension(BaseDimension):
    """
    Base class for dimensions whose inspection is simply the scalar value
    returned by `compute_single()`.

    This class is intended for dimensions that do not produce iterable
    matches, highlights, or discarded matches.
    """

    def inspect(
        self,
        row: pd.Series,
    ) -> DimensionInspection:
        """
        Build an inspection object for a single DataFrame row.

        Parameters
        ----------
        row:
            Input row represented as a pandas Series.

        Returns
        -------
        DimensionInspection
            Inspection object containing the computed scalar value
            as debug information.
        """
        value = self.compute_single(row)

        return DimensionInspection(
            key=self.key,
            class_name=self.__class__.__name__,
            pattern=None,
            dictionary=None,
            matches=[],
            discarded_matches=[],
            debug_text=f"Value: {value}",
        )