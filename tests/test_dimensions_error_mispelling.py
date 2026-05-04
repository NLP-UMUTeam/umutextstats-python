# tests/test_dimensions_error_mispelling.py

import pandas as pd
import pytest

from umutextstats.dimensions.error_mispelling import ErrorMispellingDimension


pytest.importorskip("spellchecker")


def compute(texts):
    df = pd.DataFrame({"text_norm": texts})
    dim = ErrorMispellingDimension(key="misspelling")
    return list(dim.compute(df))


def test_empty_text():
    assert compute([""]) == [0.0]


def test_valid_spanish_words_have_low_error_rate():
    assert compute(["hola mundo"])[0] <= 50.0


def test_clear_misspelling_has_some_error():
    assert compute(["hola mundooo"])[0] > 0.0