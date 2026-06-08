import pandas as pd

from umutextstats.dimensions.dependency import DependencyDistanceDimension


def compute(tagged_dep, mode="mean"):
    df = pd.DataFrame({"tagged_dep": tagged_dep})

    dim = DependencyDistanceDimension(
        key="distance",
        mode=mode,
    )

    return list(dim.compute(df))


def test_dependency_distance_mean_simple_sentence():
    tagged = [
        "María__(nsubj)(2), compra__(root)(0), libros__(obj)(2)"
    ]

    result = compute(tagged, mode="mean")

    assert result == [1.0]


def test_dependency_distance_max():
    tagged = [
        "El__(det)(2), libro__(nsubj)(5), que__(obj)(4), compré__(acl:relcl)(2), llegó__(root)(0)"
    ]

    result = compute(tagged, mode="max")

    assert result == [3.0]


def test_dependency_distance_sum():
    tagged = [
        "María__(nsubj)(2), compra__(root)(0), libros__(obj)(2)"
    ]

    result = compute(tagged, mode="sum")

    assert result == [2.0]


def test_dependency_distance_ignores_root():
    tagged = [
        "Hola__(root)(0)"
    ]

    result = compute(tagged, mode="mean")

    assert result == [0.0]


def test_dependency_distance_empty():
    assert compute([""], mode="mean") == [0.0]


def test_dependency_distance_malformed_items_are_ignored():
    tagged = [
        "María__(nsubj)(2), malformed, libros__(obj)(2)"
    ]

    result = compute(tagged, mode="mean")

    assert result == [1.0]