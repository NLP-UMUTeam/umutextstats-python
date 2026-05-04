# tests/test_dimensions_error_mispelling_accents.py

import pandas as pd

from umutextstats.dimensions.error_mispelling_accents import (
    ErrorMispellingAccentsDimension,
)


class FakeSpellChecker:
    def __init__(self):
        self._known = {"hola", "mundo", "camión", "rápido"}
        self._corrections = {
            "camion": "camión",
            "rapido": "rápido",
            "holaa": "hola",
        }

    def available(self) -> bool:
        return True

    def is_known(self, word: str) -> bool:
        return word in self._known

    def correction(self, word: str) -> str | None:
        return self._corrections.get(word)

    # opcional: mantener compatibilidad con código antiguo
    def __contains__(self, word):
        return self.is_known(word)


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