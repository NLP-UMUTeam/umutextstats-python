import pandas as pd

from umutextstats.dimensions.count import WordCountDimension


def compute(texts):
    df = pd.DataFrame({"text_norm": texts})
    dim = WordCountDimension(key="words")
    return list(dim.compute(df))


# =========================
# Casos básicos
# =========================

def test_simple_words():
    assert compute(["hola mundo"]) == [2]


def test_with_punctuation():
    assert compute(["hola, mundo."]) == [2]


def test_with_uppercase():
    assert compute(["Hola Mundo"]) == [2]


# =========================
# Edge cases
# =========================

def test_empty_string():
    assert compute([""]) == [0]


def test_only_spaces():
    assert compute(["   "]) == [0]


def test_only_punctuation():
    assert compute(["!!!"]) == [0]


def test_numbers_count():
    assert compute(["tengo 2 casas"]) == [3]


# =========================
# Casos reales
# =========================

def test_spanish_sentence():
    assert compute(["¡Hola! ¿Cómo estás?"]) == [3]


def test_accents_and_special_chars():
    assert compute(["rápido camión pingüino"]) == [3]


def test_mixed_text():
    assert compute(["Hola mundo 123!!! test"]) == [4]


# =========================
# Múltiples filas
# =========================

def test_multiple_rows():
    texts = [
        "hola mundo",
        "hola",
        "",
        "uno dos tres cuatro",
    ]

    assert compute(texts) == [2, 1, 0, 4]