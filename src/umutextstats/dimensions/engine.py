from contextlib import nullcontext

import pandas as pd
from tqdm.auto import tqdm

from umutextstats.config.models import DimensionConfig, UMUTextStatsConfig
from umutextstats.dimensions.composite import CompositeDimension
from umutextstats.dimensions.dimension_input import DimensionInput
from umutextstats.dimensions.factory import build_dimension_instance
from umutextstats.dimensions.registry import (
    normalize_class_name,
    resolve_dimension,
)


class DimensionEngine:
    def __init__(
        self,
        config: UMUTextStatsConfig,
        input_column: str = "text_norm",
        include_unimplemented: bool = True,
        profiler=None,
        show_progress: bool = True,
    ):
        self.config = config
        self.input_column = input_column
        self.include_unimplemented = include_unimplemented
        self.profiler = profiler
        self.show_progress = show_progress

    def compute(self, df) -> pd.DataFrame:
        data = {}

        if "id" in df.columns:
            data["id"] = df["id"]

        dimensions = list(self._iter_dimensions(self.config.dimensions))

        iterator = tqdm(
            dimensions,
            desc="Dimensions",
            unit="dimension",
            disable=not self.show_progress,
        )

        for dimension in iterator:
            iterator.set_postfix_str(dimension.key)
            self._compute_dimension(df, dimension, data)

        return pd.DataFrame(data)

    def _iter_dimensions(
        self,
        dimensions: list[DimensionConfig],
    ):
        for dimension in dimensions:
            yield dimension

            if dimension.children:
                yield from self._iter_dimensions(dimension.children)

    def _compute_dimension(
        self,
        df,
        dimension: DimensionConfig,
        data: dict,
    ) -> None:
        key = dimension.key

        if key in data:
            return

        class_name = normalize_class_name(dimension.class_name)

        with self._track_dimension(key, class_name):
            self._compute_children(df, dimension, data)

            if dimension.children:
                instance = CompositeDimension.from_config(
                    dimension=dimension,
                    input_column=self.input_column,
                )

                data[key] = instance.compute_from_data(
                    data=data,
                    n_rows=len(df),
                )
                return

            instance = self._build_instance(dimension)


            if instance is None:
                if self.include_unimplemented:
                    data[key] = [""] * len(df)
                return

            if hasattr(instance, "compute_from_data"):
                data[key] = instance.compute_from_data(
                    data=data,
                    n_rows=len(df),
                )
                return

            if hasattr(instance, "compute_inputs"):
                items = self._build_dimension_inputs(df)
                data[key] = instance.compute_inputs(items)
                return

            data[key] = instance.compute(df)

    def _compute_children(
        self,
        df,
        dimension: DimensionConfig,
        data: dict,
    ) -> None:
        for child in dimension.children:
            self._compute_dimension(df, child, data)

    def _build_instance(
        self,
        dimension: DimensionConfig,
    ):
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
        if self.profiler is None:
            return nullcontext()

        return self.profiler.track(
            stage="dimension",
            name=key,
            class_name=class_name or "",
        )

    def _build_dimension_inputs(
        self,
        df,
    ) -> list[DimensionInput]:
        items = []

        for _, row in df.iterrows():
            row_dict = row.to_dict()

            annotations = {
                key: value
                for key, value in row_dict.items()
                if key.startswith("tagged_")
                or key in {
                    "sentences",
                    "tokens",
                    "lemmas",
                    "dependencies",
                    "entities",
                }
            }

            items.append(
                DimensionInput(
                    row=row_dict,
                    annotations=annotations,
                )
            )

        return items