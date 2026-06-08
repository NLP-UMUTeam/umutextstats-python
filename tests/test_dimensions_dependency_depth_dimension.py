import pandas as pd

from umutextstats.dimensions.dependency import DependencyDepthDimension


def compute(tagged_dep, mode="max"):
    df = pd.DataFrame({"tagged_dep": tagged_dep})

    dim = DependencyDepthDimension(
        key="depth",
        mode=mode,
    )

    return list(dim.compute(df))


def test_dependency_depth_max_simple_sentence():
    tagged = [
        "María__(nsubj)(2), compra__(root)(0), libros__(obj)(2)"
    ]

    result = compute(tagged, mode="max")

    assert result == [1.0]


def test_dependency_depth_max_nested_sentence():
    tagged = [
        "Juan__(nsubj)(2), dijo__(root)(0), que__(mark)(5), María__(nsubj)(5), venía__(ccomp)(2)"
    ]

    result = compute(tagged, mode="max")

    assert result == [2.0]


def test_dependency_depth_mean():
    tagged = [
        "María__(nsubj)(2), compra__(root)(0), libros__(obj)(2)"
    ]

    result = compute(tagged, mode="mean")

    assert round(result[0], 2) == 0.67


def test_dependency_depth_empty():
    assert compute([""], mode="max") == [0.0]


def test_dependency_depth_malformed_items_are_ignored(): 
    tagged = [
        "María__(nsubj)(2), malformed, libros__(obj)(2)"
    ]

    result = compute(tagged, mode="max")

    assert result == [0.0]