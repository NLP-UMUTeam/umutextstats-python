# tests/test_dimensions_language.py

import pandas as pd

from umutextstats.dimensions.language import LanguageDimension


class FakeModel:
    def predict(self, text, k=2):
        if "hello" in text:
            return ["__label__en", "__label__es"], [0.9, 0.1]
        return ["__label__es", "__label__en"], [0.8, 0.2]


def compute(texts, lang):
    df = pd.DataFrame({"text_norm": texts})

    dim = LanguageDimension(key="lang", language=lang)
    dim.model = FakeModel()

    return list(dim.compute(df))


def test_spanish():
    assert compute(["hola mundo"], "es") == [0.8]


def test_english():
    assert compute(["hello world"], "en") == [0.9]


def test_not_present():
    assert compute(["hola mundo"], "fr") == [0.0]


def test_empty():
    assert compute([""], "es") == [0.0]