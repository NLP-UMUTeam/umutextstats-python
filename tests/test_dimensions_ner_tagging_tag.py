# tests/test_dimensions_ner_tagging_tag.py

import pandas as pd

from umutextstats.dimensions.ner_tagging_tag import NERTaggingTag


def compute(tagged_ner, tag, normalizer="entities"):
    df = pd.DataFrame({"tagged_ner": tagged_ner})

    dim = NERTaggingTag(
        key="ner",
        tag=tag,
        normalizer=normalizer,
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


def test_words_normalizer_single_entity_match():
    assert compute(["PER(Juan) come en Madrid"], "PER", "words") == [25.0]


def test_words_normalizer_multiple_entities():
    result = compute(
        ["PER(Juan) vive en LOC(Madrid)"],
        "PER",
        "words",
    )

    assert result == [25.0]


def test_entities_normalizer_is_default():
    result = compute(
        ["PER(Juan), LOC(Madrid), ORG(OpenAI)"],
        "PER",
    )

    assert round(result[0], 2) == 33.33


def test_entities_normalizer_explicit():
    result = compute(
        ["PER(Juan), LOC(Madrid), ORG(OpenAI)"],
        "PER",
        "entities",
    )

    assert round(result[0], 2) == 33.33


def test_words_normalizer_no_entities():
    assert compute(["Juan vive en Madrid"], "PER", "words") == [0.0]


def test_words_normalizer_empty_text():
    assert compute([""], "PER", "words") == [0.0]


def test_unknown_normalizer_raises_error():
    df = pd.DataFrame({"tagged_ner": ["PER(Juan)"]})

    dim = NERTaggingTag(
        key="ner",
        tag="PER",
        normalizer="bad-normalizer",
    )

    try:
        list(dim.compute(df))
        assert False
    except ValueError as exc:
        assert "Unknown NER normalizer" in str(exc)