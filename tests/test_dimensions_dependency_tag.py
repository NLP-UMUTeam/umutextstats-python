import pandas as pd

from umutextstats.dimensions.dependency_tag import DependencyTag


def compute(tagged_dep, deprel=None):
    df = pd.DataFrame({"tagged_dep": tagged_dep})

    dim = DependencyTag(
        key="dep",
        deprel=deprel,
    )

    return list(dim.compute(df))


def test_subject_dependencies():
    tagged = [
        "María__(nsubj)(2), compra__(root)(0), libros__(obj)(2)"
    ]

    result = compute(tagged, deprel="nsubj")

    assert round(result[0], 2) == 33.33


def test_object_dependencies():
    tagged = [
        "María__(nsubj)(2), compra__(root)(0), libros__(obj)(2)"
    ]

    result = compute(tagged, deprel="obj")

    assert round(result[0], 2) == 33.33


def test_root_dependencies():
    tagged = [
        "María__(nsubj)(2), compra__(root)(0), libros__(obj)(2)"
    ]

    result = compute(tagged, deprel="root")

    assert round(result[0], 2) == 33.33


def test_no_matching_dependency():
    tagged = [
        "María__(nsubj)(2), compra__(root)(0), libros__(obj)(2)"
    ]

    result = compute(tagged, deprel="iobj")

    assert result == [0.0]


def test_multiple_matching_dependencies():
    tagged = [
        "Juan__(nsubj)(2), María__(conj)(1), compran__(root)(0), libros__(obj)(3), pan__(obj)(3)"
    ]

    result = compute(tagged, deprel="obj")

    assert result == [40.0]


def test_empty_tagged_dep():
    assert compute([""], deprel="nsubj") == [0.0]


def test_malformed_items_are_ignored():
    tagged = [
        "María__(nsubj)(2), malformed, libros__(obj)(2)"
    ]

    result = compute(tagged, deprel="obj")

    assert result == [50.0]