import pandas as pd

from umutextstats.dimensions.rtie import RTIEDimension


def compute(texts, separator="whole", chunk_size=1000):
    df = pd.DataFrame({"text_norm": texts})

    dim = RTIEDimension(
        key="rtie",
        separator=separator,
        chunk_size=chunk_size,
    )

    return list(dim.compute(df))


def test_whole_all_unique():
    assert compute(["uno dos tres"], separator="whole") == [1.0]


def test_whole_repeated_words():
    assert compute(["uno uno dos"], separator="whole") == [2 / 3]


def test_empty_text():
    assert compute([""], separator="whole") == [0.0]


def test_by_sentence():
    result = compute(
        ["uno uno dos. tres cuatro."],
        separator="by-sentence",
    )

    # sentence1: 2 unique / 3 words = 0.666...
    # sentence2: 2 unique / 2 words = 1
    # avg = 0.833...
    assert round(result[0], 2) == 0.83


def test_by_chunks_default_behavior():
    result = compute(
        ["uno uno dos tres"],
        separator="by-chunks",
        chunk_size=2,
    )

    # chunk1: uno uno => 1/2 = 0.5
    # chunk2: dos tres => 2/2 = 1
    # avg = 0.75
    assert result == [0.75]


def test_unknown_separator_defaults_to_chunks():
    result = compute(
        ["uno uno dos tres"],
        separator="whatever",
        chunk_size=2,
    )

    assert result == [0.75]


def test_multiple_rows():
    result = compute(
        ["uno uno dos", "uno dos tres", ""],
        separator="whole",
    )

    assert result == [2 / 3, 1.0, 0.0]