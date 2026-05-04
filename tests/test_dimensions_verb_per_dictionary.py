# tests/test_dimensions_verb_per_dictionary.py

import pandas as pd

from umutextstats.dictionaries import DictionaryEntries
from umutextstats.dimensions.verb_per_dictionary import VerbPerDictionary


class DummyDictionaryLoader:
    def __init__(self, entries):
        self.entries = entries

    def load(self, name):
        return DictionaryEntries(
            words=self.entries,
            exceptions=[],
        )


def compute(texts, entries, percentage=True):
    df = pd.DataFrame({"text_norm": texts})

    dim = VerbPerDictionary(
        key="verb_dict",
        dictionary_name="dummy",
        percentage=percentage,
        dictionary_loader=DummyDictionaryLoader(entries),
    )

    return list(dim.compute(df))


def test_simple_verb_match():
    assert compute(["como pan"], ["como"], percentage=False) == [1]


def test_no_match():
    assert compute(["como pan"], ["bebo"], percentage=False) == [0]


def test_compound_verb_with_haber():
    assert compute(
        ["he comido pan"],
        ["he comido"],
        percentage=False,
    ) == [1]


def test_compound_verb_with_haber_accented():
    assert compute(
        ["había comido pan"],
        ["había comido"],
        percentage=False,
    ) == [1]


def test_haber_does_not_persist_beyond_next_word():
    assert compute(
        ["he pan comido"],
        ["he comido"],
        percentage=False,
    ) == [0]


def test_percentage():
    result = compute(
        ["he comido pan"],
        ["he comido"],
        percentage=True,
    )

    assert round(result[0], 2) == 33.33


def test_multiple_matches():
    assert compute(
        ["he comido y he bebido"],
        ["he comido", "he bebido"],
        percentage=False,
    ) == [2]


def test_empty_text():
    assert compute([""], ["he comido"], percentage=False) == [0.0]