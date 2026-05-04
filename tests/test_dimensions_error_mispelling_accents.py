# tests/test_dimensions_error_mispelling_accents.py

import pandas as pd

from umutextstats.dimensions.error_mispelling_accents import (
    ErrorMispellingAccentsDimension,
)


class FakeSpellChecker:
    def __contains__(self, word):
        return word in {"hola", "mundo", "camión", "rápido"}

    def correction(self, word):
        corrections = {
            "camion": "camión",
            "rapido": "rápido",
            "holaa": "hola",
        }
        return corrections.get(word)


def compute(texts):
    df = pd.DataFrame({"text_norm": texts})

    dim = ErrorMispellingAccentsDimension(key="accents")
    dim.spellchecker = FakeSpellChecker()

    return list(dim.compute(df))


def test_detects_missing_accent():
    assert compute(["camion"]) == [100.0]


def test_detects_multiple_missing_accents():
    assert compute(["camion rapido"]) == [100.0]


def test_does_not_count_non_accent_misspelling():
    assert compute(["holaa"]) == [0.0]


def test_mixed_words():
    result = compute(["hola camion mundo"])
    assert round(result[0], 2) == 33.33


def test_empty_text():
    assert compute([""]) == [0.0]