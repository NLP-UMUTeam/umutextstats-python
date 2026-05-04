

import pandas as pd

from umutextstats.dimensions.word_case import WordCase


def compute(texts, comparator="upper"):
    df = pd.DataFrame({"text_raw": texts})
    dim = WordCase(key="case", comparator=comparator)
    return list(dim.compute(df))


def test_uppercase_all_words():
    assert compute(["HOLA MUNDO"], "upper") == [100.0]


def test_uppercase_partial():
    assert compute(["HOLA mundo"], "upper") == [50.0]


def test_lowercase_all_words():
    assert compute(["hola mundo"], "lower") == [100.0]


def test_lowercase_partial():
    assert compute(["hola MUNDO"], "lower") == [50.0]


def test_titlecase_all_words():
    assert compute(["Hola Mundo"], "title") == [100.0]


def test_titlecase_filters_short_words_after_first():
    assert compute(["Hola de Mundo"], "title") == [100.0]


def test_titlecase_first_short_word_is_kept():
    assert compute(["El Mundo"], "title") == [100.0]


def test_titlecase_partial():
    assert compute(["Hola mundo Grande"], "title") == [66.66666666666667]


def test_numbers_are_excluded():
    assert compute(["HOLA 123 MUNDO"], "upper") == [100.0]


def test_beginning_mention_is_removed():
    assert compute(["@user HOLA MUNDO"], "upper") == [100.0]


def test_url_is_removed():
    assert compute(["HOLA https://example.com MUNDO"], "upper") == [100.0]


def test_empty_text():
    assert compute([""], "upper") == [0.0]