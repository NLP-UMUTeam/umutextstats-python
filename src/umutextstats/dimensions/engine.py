from contextlib import nullcontext

import pandas as pd
from tqdm.auto import tqdm

from umutextstats.config.models import DimensionConfig, UMUTextStatsConfig
from umutextstats.dimensions.composite import CompositeDimension
from umutextstats.dimensions.factory import build_dimension_instance
from umutextstats.dimensions.registry import (
    normalize_class_name,
    resolve_dimension,
)


class DimensionEngine:
    """
    Engine responsible for computing all configured dimensions.

    The engine works with pandas DataFrames as the runtime context.
    Each regular dimension receives the full input DataFrame through
    `compute(df)`.

    Composite-like dimensions can use already computed results through
    `compute_from_data(data, n_rows)`.
    """

    def __init__(
        self,
        config: UMUTextStatsConfig,
        input_column: str = "text_norm",
        include_unimplemented: bool = True,
        profiler=None,
        show_progress: bool = True,
    ):
        """
        Initialize the dimension engine.

        Parameters
        ----------
        config:
            UMUTextStats configuration containing the dimension tree.
        input_column:
            Default input column passed to dimension factories.
        include_unimplemented:
            If True, unresolved dimensions are included as empty columns.
        profiler:
            Optional profiler used to track dimension execution.
        show_progress:
            Whether to show a tqdm progress bar.
        """
        self.config = config
        self.input_column = input_column
        self.include_unimplemented = include_unimplemented
        self.profiler = profiler
        self.show_progress = show_progress

    def compute(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Compute all configured dimensions for the input DataFrame.

        Parameters
        ----------
        df:
            Input DataFrame containing text and annotation columns.

        Returns
        -------
        pd.DataFrame
            Output DataFrame with one column per computed dimension.
        """
        data = {}

        if "id" in df.columns:
            data["id"] = df["id"]

        dimensions = list(
            self._iter_dimensions(self.config.dimensions)
        )

        iterator = tqdm(
            dimensions,
            desc="Dimensions",
            unit="dimension",
            disable=not self.show_progress,
        )

        for dimension in iterator:
            iterator.set_postfix_str(dimension.key)
            self._compute_dimension(
                df=df,
                dimension=dimension,
                data=data,
            )

        return pd.DataFrame(data)

    def _iter_dimensions(
        self,
        dimensions: list[DimensionConfig],
    ):
        """
        Yield dimensions recursively, including children.

        Children are yielded so they can also appear as individual
        output columns and be reused by composite dimensions.
        """
        for dimension in dimensions:
            yield dimension

            if dimension.children:
                yield from self._iter_dimensions(dimension.children)

    def _compute_dimension(
        self,
        df: pd.DataFrame,
        dimension: DimensionConfig,
        data: dict,
    ) -> None:
        """
        Compute one dimension and store its result in `data`.

        The engine supports two execution paths:

        1. Regular dimensions:
           `compute(df)`

        2. Dimensions based on previously computed outputs:
           `compute_from_data(data, n_rows)`
        """
        key = dimension.key

        if key in data:
            return

        class_name = normalize_class_name(dimension.class_name)

        with self._track_dimension(
            key=key,
            class_name=class_name,
        ):
            self._compute_children(
                df=df,
                dimension=dimension,
                data=data,
            )

            if dimension.children:
                self._compute_composite_dimension(
                    dimension=dimension,
                    data=data,
                    n_rows=len(df),
                )
                return

            instance = self._build_instance(dimension)

            if instance is None:
                self._handle_unimplemented_dimension(
                    key=key,
                    data=data,
                    n_rows=len(df),
                )
                return

            if hasattr(instance, "compute_from_data"):
                data[key] = instance.compute_from_data(
                    data=data,
                    n_rows=len(df),
                )
                return

            data[key] = instance.compute(df)

    def _compute_children(
        self,
        df: pd.DataFrame,
        dimension: DimensionConfig,
        data: dict,
    ) -> None:
        """
        Compute all child dimensions before their parent.

        This is required because composite dimensions depend on the
        already computed values of their children.
        """
        for child in dimension.children:
            self._compute_dimension(
                df=df,
                dimension=child,
                data=data,
            )

    def _compute_composite_dimension(
        self,
        dimension: DimensionConfig,
        data: dict,
        n_rows: int,
    ) -> None:
        """
        Compute a dimension that has children.

        Parent dimensions with children are represented as
        CompositeDimension instances and are computed from the child
        outputs already stored in `data`.
        """
        instance = CompositeDimension.from_config(
            dimension=dimension,
            input_column=self.input_column,
        )

        data[dimension.key] = instance.compute_from_data(
            data=data,
            n_rows=n_rows,
        )

    def _handle_unimplemented_dimension(
        self,
        key: str,
        data: dict,
        n_rows: int,
    ) -> None:
        """
        Add an empty output column for an unresolved dimension.

        This keeps the output shape stable when `include_unimplemented`
        is enabled.
        """
        if self.include_unimplemented:
            data[key] = [""] * n_rows

    def _build_instance(
        self,
        dimension: DimensionConfig,
    ):
        """
        Build a dimension instance from its configuration.

        Returns None when the dimension has no class name or when the
        class cannot be resolved from the registry.
        """
        if not dimension.class_name:
            return None

        dimension_cls = resolve_dimension(dimension.class_name)

        if dimension_cls is None:
            return None

        return build_dimension_instance(
            dimension=dimension,
            dimension_cls=dimension_cls,
            default_input_column=self.input_column,
        )

    def _track_dimension(
        self,
        key: str,
        class_name: str | None,
    ):
        """
        Return a profiler context for a dimension computation.

        If no profiler is configured, a no-op context manager is used.
        """
        if self.profiler is None:
            return nullcontext()

        return self.profiler.track(
            stage="dimension",
            name=key,
            class_name=class_name or "",
        )