# tests/test_dimensions_error_capitalization.py

import pandas as pd

from umutextstats.dimensions.error_capitalization import (
    ErrorCapitalizationStartingWithLowerCaseDimension,
)


def compute(texts):
    df = pd.DataFrame({"text_raw": texts})
    dim = ErrorCapitalizationStartingWithLowerCaseDimension(key="capitalization")
    return list(dim.compute(df))


def test_sentence_starts_uppercase():
    assert compute(["Hola mundo."]) == [0.0]


def test_sentence_starts_lowercase():
    assert compute(["hola mundo."]) == [100.0]


def test_two_sentences_one_error():
    assert compute(["Hola mundo. esto falla."]) == [50.0]


def test_spanish_opening_exclamation_is_ignored():
    assert compute(["¡hola mundo!"]) == [100.0]


def test_spanish_opening_question_uppercase():
    assert compute(["¿Hola mundo?"]) == [0.0]


def test_mentions_are_removed_before_checking():
    assert compute(["@user Hola mundo."]) == [0.0]


def test_mentions_then_lowercase():
    assert compute(["@user hola mundo."]) == [100.0]


def test_starting_quote_is_ignored():
    assert compute(['"hola mundo."']) == [100.0]


def test_empty_text():
    assert compute([""]) == [0.0]


def test_numbers_do_not_count_as_lowercase_error():
    assert compute(["123 hola mundo."]) == [0.0]