import pandas as pd

from umutextstats.dimensions.passive_voice_dependency import PassiveVoiceDependencyDimension


def compute(tagged_dep):
    df = pd.DataFrame({
        "tagged_dep": tagged_dep,
    })

    dim = PassiveVoiceDependencyDimension(
        key="passive",
    )

    return list(dim.compute(df))


def test_detects_aux_pass():
    tagged = [
        (
            "La__(det)(2), carta__(nsubj:pass)(4), "
            "fue__(aux:pass)(4), escrita__(root)(0)"
        )
    ]

    result = compute(tagged)

    assert result == [100.0]


def test_detects_nsubj_pass():
    tagged = [
        (
            "Los__(det)(2), libros__(nsubj:pass)(4), "
            "fueron__(aux)(4), vendidos__(root)(0)"
        )
    ]

    result = compute(tagged)

    assert result == [100.0]


def test_detects_expl_pass():
    tagged = [
        (
            "Se__(expl:pass)(2), vende__(root)(0), "
            "casa__(obj)(2)"
        )
    ]

    result = compute(tagged)

    assert result == [100.0]


def test_active_voice_returns_zero():
    tagged = [
        (
            "Juan__(nsubj)(2), come__(root)(0), "
            "pan__(obj)(2)"
        )
    ]

    result = compute(tagged)

    assert result == [0.0]


def test_mixed_sentences():
    tagged = [
        (
            "Juan__(nsubj)(2), come__(root)(0) || "
            "La__(det)(2), carta__(nsubj:pass)(4), "
            "fue__(aux:pass)(4), escrita__(root)(0)"
        )
    ]

    result = compute(tagged)

    assert result == [50.0]


def test_empty_input():
    result = compute([""])

    assert result == [0.0]