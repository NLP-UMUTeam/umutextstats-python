# tests/test_dimensions_rtie_deviation.py

import pandas as pd

from umutextstats.dimensions.rtie import RTIEDeviationDimension


def compute(texts, separator="by-chunks", chunk_size=1000):
    df = pd.DataFrame({"text_norm": texts})

    dim = RTIEDeviationDimension(
        key="rtie_deviation",
        separator=separator,
        chunk_size=chunk_size,
    )

    return list(dim.compute(df))


def test_empty_text():
    assert compute([""]) == [0.0]


def test_whole_has_zero_deviation():
    assert compute(["uno uno dos"], separator="whole") == [0.0]


def test_by_sentence_deviation():
    result = compute(
        ["uno uno dos. tres cuatro."],
        separator="by-sentence",
    )

    # ratios: 2/3 and 1.0
    # population std dev = 0.166666...
    assert round(result[0], 2) == 0.17


def test_by_chunks_deviation():
    result = compute(
        ["uno uno dos tres"],
        separator="by-chunks",
        chunk_size=2,
    )

    # ratios: 0.5 and 1.0
    # population std dev = 0.25
    assert result == [0.25]


def test_multiple_rows():
    result = compute(
        ["uno uno dos tres", "", "uno dos tres"],
        separator="by-chunks",
        chunk_size=2,
    )

    assert result == [0.25, 0.0, 0.0]