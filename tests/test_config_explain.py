# tests/test_config_explain.py

from umutextstats.config.explain import (
    find_dimension,
    render_dimension_explanation,
    explanation_to_dict
)
from umutextstats.config.models import DimensionConfig, UMUTextStatsConfig



def test_find_dimension_returns_path():
    config = UMUTextStatsConfig(
        dimensions=[
            DimensionConfig(
                key="morphosyntax",
                children=[
                    DimensionConfig(
                        key="morphosyntax-gender",
                        children=[
                            DimensionConfig(
                                key="morphosyntax-gender-feminine",
                                class_name="POSTaggingTag",
                                universal="Gender=Fem",
                                description="Feminine words",
                            )
                        ],
                    )
                ],
            )
        ]
    )

    explanation = find_dimension(config, "morphosyntax-gender-feminine")

    assert explanation is not None
    assert explanation.path == [
        "morphosyntax",
        "morphosyntax-gender",
        "morphosyntax-gender-feminine",
    ]


def test_render_dimension_explanation():
    config = UMUTextStatsConfig(
        dimensions=[
            DimensionConfig(
                key="x",
                class_name="POSTaggingTag",
                universal="Gender=Fem",
                description="Feminine words",
            )
        ]
    )

    explanation = find_dimension(config, "x")

    assert explanation is not None

    text = render_dimension_explanation(explanation)

    assert "Key: x" in text
    assert "Class: POSTaggingTag" in text
    assert "Description: Feminine words" in text
    assert "universal: Gender=Fem" in text


def test_explanation_to_dict_includes_parent_and_children_count():
    config = UMUTextStatsConfig(
        dimensions=[
            DimensionConfig(
                key="parent",
                children=[
                    DimensionConfig(
                        key="child",
                        class_name="POSTaggingTag",
                        params={"tag": "PRON"},
                    )
                ],
            )
        ]
    )

    explanation = find_dimension(config, "child")

    assert explanation is not None

    data = explanation_to_dict(explanation)

    assert data["key"] == "child"
    assert data["path"] == ["parent", "child"]
    assert data["parent"] == "parent"
    assert data["children_count"] == 0
    assert data["children"] == []
    assert data["parameters"] == {"tag": "PRON"}


def test_render_dimension_explanation_includes_parent_and_children_count():
    config = UMUTextStatsConfig(
        dimensions=[
            DimensionConfig(
                key="parent",
                children=[
                    DimensionConfig(key="child")
                ],
            )
        ]
    )

    explanation = find_dimension(config, "parent")

    assert explanation is not None

    text = render_dimension_explanation(explanation)

    assert "Children count: 1" in text
    assert "Children:" in text
    assert "- child" in text