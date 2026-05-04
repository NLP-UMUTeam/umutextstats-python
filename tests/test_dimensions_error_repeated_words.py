# tests/test_dimensions_error_repeated_words.py

import pandas as pd

from umutextstats.dimensions.error_repeated_words import (
    ErrorMiscTwoOrMoreEqualWordsDimension,
)


def compute(texts):
    df = pd.DataFrame({"text_norm": texts})
    dim = ErrorMiscTwoOrMoreEqualWordsDimension(key="repeated")
    return list(dim.compute(df))


def test_no_repeated_words():
    assert compute(["hola mundo."]) == [0.0]


def test_one_repeated_word():
    assert compute(["hola hola mundo."]) == [100.0]


def test_two_repeated_words_same_sentence():
    assert compute(["hola hola mundo mundo."]) == [200.0]


def test_one_repeated_word_two_sentences():
    assert compute(["hola hola mundo. adiós mundo."]) == [50.0]


def test_case_insensitive():
    assert compute(["Hola hola mundo."]) == [100.0]


def test_empty_text():
    assert compute([""]) == [0.0]


def test_repeated_with_punctuation_between():
    assert compute(["hola, hola mundo."]) == [100.0]


def test_multiple_rows():
    assert compute(["hola hola.", "hola mundo.", ""]) == [100.0, 0.0, 0.0]