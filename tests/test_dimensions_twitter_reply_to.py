# tests/test_dimensions_twitter_reply_to.py

import pandas as pd

from umutextstats.dictionaries import DictionaryEntries
from umutextstats.dimensions.twitter_reply_to import TwitterReplyToDimension


class DummyDictionaryLoader:
    def __init__(self, entries):
        self.entries = entries

    def load(self, name):
        return DictionaryEntries(
            words=self.entries,
            exceptions=[],
        )


def compute(texts, entries):
    df = pd.DataFrame({"text_raw": texts})

    dim = TwitterReplyToDimension(
        key="twitter_reply",
        dictionary_name="dummy",
        dictionary_loader=DummyDictionaryLoader(entries),
    )

    return list(dim.compute(df))


def test_reply_to_matching_user():
    assert compute(["@usuario hola"], ["usuario"]) == [1]


def test_reply_to_non_matching_user():
    assert compute(["@otro hola"], ["usuario"]) == [0]


def test_not_reply_if_mention_not_first_token():
    assert compute(["hola @usuario"], ["usuario"]) == [0]


def test_accent_insensitive_match():
    assert compute(["@jose hola"], ["josé"]) == [1]


def test_substring_match_like_php():
    assert compute(["@usuario_123 hola"], ["usuario"]) == [1]


def test_empty_text():
    assert compute([""], ["usuario"]) == [0]


def test_multiple_rows():
    assert compute(
        ["@usuario hola", "hola @usuario", "@otro hola"],
        ["usuario"],
    ) == [1, 0, 0]