# tests/test_dimensions_ner_tagging_tag.py

import pandas as pd

from umutextstats.dimensions.ner_tagging_tag import NERTaggingTag


def compute(tagged_ner, tag):
    df = pd.DataFrame({"tagged_ner": tagged_ner})

    dim = NERTaggingTag(
        key="ner",
        tag=tag,
    )

    return list(dim.compute(df))


def test_single_entity_match():
    assert compute(["PER(Juan)"], "PER") == [100.0]


def test_single_entity_no_match():
    assert compute(["LOC(Madrid)"], "PER") == [0.0]


def test_multiple_entities():
    result = compute(["PER(Juan), LOC(Madrid), ORG(OpenAI)"], "PER")
    assert round(result[0], 2) == 33.33


def test_multiple_same_entities():
    result = compute(["PER(Juan), PER(María), LOC(Madrid)"], "PER")
    assert round(result[0], 2) == 66.67


def test_empty_ner():
    assert compute([""], "PER") == [0.0]


def test_missing_tag():
    df = pd.DataFrame({"tagged_ner": ["PER(Juan)"]})
    dim = NERTaggingTag(key="ner", tag=None)

    assert list(dim.compute(df)) == [0.0]