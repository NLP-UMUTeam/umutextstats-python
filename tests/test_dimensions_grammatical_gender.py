import pandas as pd

from umutextstats.dictionaries import DictionaryEntries
from umutextstats.dimensions.grammatical_gender import GrammaticalGenderDimension


class DummyDictionaryLoader:
    def __init__(self, entries, exceptions=None):
        self.entries = entries
        self.exceptions = exceptions or []

    def load(self, name):
        return DictionaryEntries(
            words=self.entries,
            exceptions=self.exceptions,
        )


def compute(tagged_pos, entries, exceptions=None, percentage=True):
    df = pd.DataFrame({"tagged_pos": tagged_pos})

    dim = GrammaticalGenderDimension(
        key="gender",
        dictionary_name="dummy",
        dictionary_loader=DummyDictionaryLoader(entries, exceptions),
        percentage=percentage,
    )

    return list(dim.compute(df))


def test_matches_only_allowed_pos():
    tagged = [
        "casa__(NOUN)(Gender=Fem), "
        "bonita__(ADJ)(Gender=Fem), "
        "y__(CCONJ)(), "
        "rápidamente__(ADV)()"
    ]

    result = compute(
        tagged,
        entries=["casa", "bonita", "rápidamente"],
    )

    assert result == [100.0]


def test_denominator_uses_only_allowed_pos():
    tagged = [
        "casa__(NOUN)(Gender=Fem), "
        "bonita__(ADJ)(Gender=Fem), "
        "perro__(NOUN)(Gender=Masc), "
        "y__(CCONJ)()"
    ]

    result = compute(
        tagged,
        entries=["casa", "bonita"],
    )

    assert round(result[0], 2) == 66.67


def test_no_allowed_pos():
    tagged = [
        "y__(CCONJ)(), "
        "pero__(CCONJ)(), "
        "rápidamente__(ADV)()"
    ]

    result = compute(tagged, entries=["rápidamente"])

    assert result == [0.0]


def test_exceptions_are_subtracted():
    tagged = [
        "casa__(NOUN)(Gender=Fem), "
        "bonita__(ADJ)(Gender=Fem), "
        "perra__(NOUN)(Gender=Fem)"
    ]

    result = compute(
        tagged,
        entries=["casa", "bonita", "perra"],
        exceptions=["perra"],
    )

    assert round(result[0], 2) == 66.67


def test_absolute_count():
    tagged = [
        "casa__(NOUN)(Gender=Fem), "
        "bonita__(ADJ)(Gender=Fem), "
        "perro__(NOUN)(Gender=Masc)"
    ]

    result = compute(
        tagged,
        entries=["casa", "bonita"],
        percentage=False,
    )

    assert result == [2]