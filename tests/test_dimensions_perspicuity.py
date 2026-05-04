# tests/test_dimensions_perspicuity.py

import pandas as pd

from umutextstats.dimensions.perspicuity import PerspicuityDimension


def compute(texts):
    df = pd.DataFrame({"text_norm": texts})
    dim = PerspicuityDimension(key="perspicuity")
    return list(dim.compute(df))


def test_empty_text():
    assert compute([""]) == [0.0]


def test_text_without_punctuation_counts_as_one_sentence():
    result = compute(["hola mundo"])

    # hola mundo = 2 palabras, 4 sílabas, 1 frase
    expected = 206.835 - (62.3 * (4 / 2)) - (2 / 1)

    assert result == [expected]


def test_simple_text():
    result = compute(["hola mundo."])

    expected = 206.835 - (62.3 * (4 / 2)) - (2 / 1)

    assert result == [expected]


def test_two_sentences():
    result = compute(["hola mundo. casa bonita."])

    # hola mundo casa bonita = 4 palabras
    # hola(2) mundo(2) casa(2) bonita(3) = 9 sílabas
    # 2 frases
    expected = 206.835 - (62.3 * (9 / 4)) - (4 / 2)

    assert result == [expected]


def test_multiple_rows():
    result = compute(["hola mundo.", ""])

    assert result[0] > 0
    assert result[1] == 0.0