from abc import ABC, abstractmethod
from typing import Any

from umutextstats.dimensions.dimension_input import DimensionInput


class BaseDimension(ABC):
    def __init__(self, key: str, input_column: str = "text_norm"):
        self.key = key
        self.input_column = input_column

    @abstractmethod
    def compute(self, df):
        pass

    def compute_single(self, item: DimensionInput) -> Any:
        raise NotImplementedError(
            f"{self.__class__.__name__}.compute_single() is not implemented"
        )

    def inspect(self, item: DimensionInput):
        return None

    def get_text(self, item: DimensionInput) -> str:
        return item.get_text(self.input_column)