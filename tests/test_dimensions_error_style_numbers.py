import pandas as pd

from umutextstats.dimensions.error_style_numbers import (
    ErrorStyleSentencesStartingWithNumbers,
)


def compute(texts):
    df = pd.DataFrame({"text_raw": texts})
    dim = ErrorStyleSentencesStartingWithNumbers(key="number_start")
    return list(dim.compute(df))


def test_sentence_starts_with_number():
    assert compute(["2024 fue un buen año."]) == [100.0]


def test_sentence_does_not_start_with_number():
    assert compute(["El año 2024 fue bueno."]) == [0.0]


def test_two_sentences_one_starts_with_number():
    assert compute(["Hola mundo. 2024 fue bueno."]) == [50.0]


def test_ignores_opening_symbols_before_number():
    assert compute(['"2024 fue bueno."']) == [100.0]


def test_empty_text():
    assert compute([""]) == [0.0]


def test_decimal_number_starts_sentence():
    assert compute(["3,14 es pi."]) == [100.0]


def test_punctuation_only():
    assert compute(["!!!"]) == [0.0]


def test_multiple_rows():
    assert compute(["2024 hola.", "Hola 2024.", ""]) == [100.0, 0.0, 0.0]