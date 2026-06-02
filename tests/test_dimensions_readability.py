# tests/test_dimensions_readability.py

import pandas as pd

from umutextstats.dimensions.readability import ReadabilityDimension


def compute(texts):
    df = pd.DataFrame({"text_norm": texts})
    dim = ReadabilityDimension(key="readability")
    return list(dim.compute(df))


def test_empty():
    assert compute([""]) == [0.0]


def test_simple():
    result = compute(["hola mundo."])

    expected = 206.84 - (60 * (4 / 2)) - (102 * (1 / 2))

    assert result == [expected]


def test_two_sentences():
    result = compute(["hola mundo. casa bonita."])

    # 4 palabras, 9 sílabas, 2 frases
    expected = 206.84 - (60 * (9 / 4)) - (102 * (2 / 4))

    assert result == [expected]