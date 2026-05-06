import pandas as pd

from umutextstats.dimensions.average_word_length import AverageWordLengthDimension


def compute(texts):
    df = pd.DataFrame({"text_norm": texts})
    dim = AverageWordLengthDimension(key="avg_word_length") 
    return list(dim.compute(df))


def test_average_word_length_simple():
    assert compute(["hola mundo"]) == [4.5]


def test_average_word_length_different_lengths():
    assert compute(["yo casa"]) == [3.0]


def test_average_word_length_ignores_numbers():
    assert compute(["yo tengo 2 casas"]) == [3.25]


def test_average_word_length_empty():
    assert compute([""]) == [0.0]


def test_average_word_length_punctuation():
    assert compute(["hola, mundo!"]) == [4.5]