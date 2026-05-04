# tests/test_dimensions_words_per_sentence.py

import pandas as pd

from umutextstats.dimensions.words_per_sentence import WordPerSentenceDimension


def compute(texts):
    df = pd.DataFrame({"text_norm": texts})
    dim = WordPerSentenceDimension(key="wps")
    return list(dim.compute(df))


def test_empty():
    assert compute([""]) == [0.0]


def test_simple():
    # 2 words / 1 sentence
    assert compute(["hola mundo."]) == [2.0]


def test_two_sentences():
    # 4 words / 2 sentences
    assert compute(["hola mundo. casa bonita."]) == [2.0] 


def test_no_punctuation_counts_as_one_sentence():
    assert compute(["hola mundo casa"]) == [3.0]


def test_multiple_rows():
    assert compute(["hola mundo.", "", "uno dos tres."]) == [2.0, 0.0, 3.0]