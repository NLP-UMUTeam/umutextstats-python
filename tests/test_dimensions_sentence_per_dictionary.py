# tests/test_dimensions_sentence_per_dictionary.py

import pandas as pd

from umutextstats.dictionaries import DictionaryEntries
from umutextstats.dimensions.sentence_per_dictionary import SentencePerDictionary


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

    dim = SentencePerDictionary(
        key="sentence_dict",
        dictionary_name="dummy",
        percentage=percentage,
        dictionary_loader=DummyDictionaryLoader(entries),
    )

    return list(dim.compute(df))


def test_one_match_one_sentence():
    assert compute(["hola mundo."], ["hola"]) == [100.0]


def test_no_match():
    assert compute(["hola mundo."], ["adiós"]) == [0.0]


def test_one_match_two_sentences():
    assert compute(["hola mundo. adiós mundo."], ["hola"]) == [50.0]


def test_two_matches_one_sentence_can_exceed_100():
    assert compute(["hola hola mundo."], ["hola"]) == [200.0]


def test_without_percentage():
    assert compute(["hola mundo. hola otra vez."], ["hola"], percentage=False) == [2]


def test_regex_dictionary():
    result = compute(
        ["logro algo. logramos mucho."],
        ["logr\\p{L}+"],
    )

    assert result == [100.0]


def test_empty_text():
    assert compute([""], ["hola"]) == [0.0]