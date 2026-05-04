# tests/test_dimensions_syllable_per_word.py

import pandas as pd

from umutextstats.dimensions.syllable_per_word import SyllablePerWordDimension


def compute(texts):
    df = pd.DataFrame({"text_norm": texts})
    dim = SyllablePerWordDimension(key="syllable_per_word")
    return list(dim.compute(df))


def test_empty_text():
    assert compute([""]) == [0.0]


def test_simple_text():
    # hola(2) mundo(2) / 2 words = 2
    assert compute(["hola mundo"]) == [2.0]


def test_different_word_lengths():
    # casa(2) bonita(3) / 2 words = 2.5
    assert compute(["casa bonita"]) == [2.5]


def test_ignores_numbers():
    # hola(2) mundo(2), 2 is ignored
    assert compute(["hola 2 mundo"]) == [2.0]


def test_multiple_rows():
    assert compute(["hola mundo", "", "casa bonita"]) == [2.0, 0.0, 2.5]