# src/umutextstats/dimensions/pos_tagging_expression.py

from umutextstats.dimensions.pattern import PatternDimension


class POSTaggingExpression(PatternDimension):
    def __init__(
        self,
        key: str,
        pattern: str,
        input_column: str = "tagged_pos",
        percentage: bool = True,
    ):
        super().__init__(
            key=key,
            pattern=pattern,
            input_column=input_column,
            percentage=percentage,
        )