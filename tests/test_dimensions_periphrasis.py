# tests/test_dimensions_periphrasis.py

import pandas as pd

from umutextstats.dimensions.periphrasis import PeriphrasisDimension


def compute(text, tagged_pos, auxiliar_verbs):
    df = pd.DataFrame(
        {
            "text_norm": [text],
            "tagged_pos": [tagged_pos],
        }
    )

    dim = PeriphrasisDimension(
        key="periphrasis",
        auxiliar_verbs=auxiliar_verbs,
    )

    return list(dim.compute(df))


def test_infinitive_with_single_word_linker():
    result = compute(
        text="tengo que comer",
        tagged_pos=(
            "tengo__(AUX)(Mood=Ind), "
            "que__(SCONJ)(), "
            "comer__(VERB)(VerbForm=Inf)"
        ),
        auxiliar_verbs="tengo(que)+infinitive",
    )

    assert result == [1]


def test_infinitive_with_multiword_linker():
    result = compute(
        text="estoy a punto de salir",
        tagged_pos=(
            "estoy__(AUX)(Mood=Ind), "
            "a__(ADP)(), "
            "punto__(NOUN)(), "
            "de__(ADP)(), "
            "salir__(VERB)(VerbForm=Inf)"
        ),
        auxiliar_verbs="estoy(por|para|a punto de)+infinitive",
    )

    assert result == [1]


def test_infinitive_with_alternative_linker():
    result = compute(
        text="estoy por salir",
        tagged_pos=(
            "estoy__(AUX)(Mood=Ind), "
            "por__(ADP)(), "
            "salir__(VERB)(VerbForm=Inf)"
        ),
        auxiliar_verbs="estoy(por|para|a punto de)+infinitive",
    )

    assert result == [1]


def test_gerund_without_linker():
    result = compute(
        text="estoy comiendo",
        tagged_pos=(
            "estoy__(AUX)(Mood=Ind), "
            "comiendo__(VERB)(VerbForm=Ger)"
        ),
        auxiliar_verbs="estoy+gerund",
    )

    assert result == [1]


def test_participle_without_linker():
    result = compute(
        text="tengo hecho",
        tagged_pos=(
            "tengo__(AUX)(Mood=Ind), "
            "hecho__(VERB)(VerbForm=Part)"
        ),
        auxiliar_verbs="tengo+participe",
    )

    assert result == [1]


def test_no_match_wrong_linker():
    result = compute(
        text="tengo para comer",
        tagged_pos=(
            "tengo__(AUX)(Mood=Ind), "
            "para__(ADP)(), "
            "comer__(VERB)(VerbForm=Inf)"
        ),
        auxiliar_verbs="tengo(que)+infinitive",
    )

    assert result == [0]


def test_no_match_wrong_verb_form():
    result = compute(
        text="estoy comer",
        tagged_pos=(
            "estoy__(AUX)(Mood=Ind), "
            "comer__(VERB)(VerbForm=Inf)"
        ),
        auxiliar_verbs="estoy+gerund",
    )

    assert result == [0]


def test_multiple_periphrases():
    result = compute(
        text="tengo que comer y estoy comiendo",
        tagged_pos=(
            "tengo__(AUX)(Mood=Ind), "
            "que__(SCONJ)(), "
            "comer__(VERB)(VerbForm=Inf), "
            "y__(CCONJ)(), "
            "estoy__(AUX)(Mood=Ind), "
            "comiendo__(VERB)(VerbForm=Ger)"
        ),
        auxiliar_verbs="tengo(que)+infinitive,estoy+gerund",
    )

    assert result == [2] 


def test_empty_text():
    result = compute(
        text="",
        tagged_pos="",
        auxiliar_verbs="estar+gerund",
    )

    assert result == [0]