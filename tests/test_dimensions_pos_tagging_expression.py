# tests/test_dimensions_pos_tagging_expression.py

import pandas as pd

from umutextstats.dimensions.pos_tagging_expression import POSTaggingExpression


def compute(tagged_pos, pattern, percentage=True):
    df = pd.DataFrame({"tagged_pos": tagged_pos})

    dim = POSTaggingExpression(
        key="pos_expr",
        pattern=pattern,
        percentage=percentage,
    )

    return list(dim.compute(df))


def test_pos_expression_count_without_percentage():
    result = compute(
        ["yo__(PRON)(), como__(VERB)(Mood=Ind), pan__(NOUN)()"],
        pattern=r"__\(VERB\)",
        percentage=False,
    )

    assert result == [1]


def test_pos_expression_percentage():
    tagged = "yo__(PRON)(), como__(VERB)()"
    result = compute([tagged], pattern=r"__\(VERB\)", percentage=True)

    expected = (100 * 1) / len(tagged)

    assert result == [expected]


def test_pos_expression_no_match():
    result = compute(
        ["yo__(PRON)(), pan__(NOUN)()"],
        pattern=r"__\(VERB\)",
        percentage=False,
    )

    assert result == [0]


def test_empty_tagged_pos():
    result = compute([""], pattern=r"__\(VERB\)", percentage=True)

    assert result == [0.0]