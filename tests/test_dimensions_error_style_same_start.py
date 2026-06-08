import pandas as pd

from umutextstats.dimensions.error import (
    ErrorStyleSentencesStartingWithTheSameWord,
)


def compute(texts):
    df = pd.DataFrame({"text_raw": texts})
    dim = ErrorStyleSentencesStartingWithTheSameWord(key="same_start")
    return list(dim.compute(df))


def test_no_repeated_sentence_start():
    assert compute(["Hola mundo. Adiós mundo."]) == [0.0]


def test_repeated_sentence_start():
    assert compute(["Hola mundo. Hola otra vez."]) == [100.0]


def test_two_of_three_sentences_start_same():
    assert compute(["Hola mundo. Adiós mundo. Hola otra vez."]) == [66.66666666666667]


def test_case_insensitive():
    assert compute(["Hola mundo. hola otra vez."]) == [100.0]


def test_ignores_opening_symbols():
    assert compute(['"Hola mundo." ¿Hola otra vez?']) == [100.0]


def test_empty_text():
    assert compute([""]) == [0.0]


def test_single_sentence():
    assert compute(["Hola mundo."]) == [0.0]


def test_punctuation_only():
    assert compute(["!!!"]) == [0.0]


def test_multiple_rows():
    assert compute([
        "Hola mundo. Hola otra vez.",
        "Uno. Dos.",
        "",
    ]) == [100.0, 0.0, 0.0]