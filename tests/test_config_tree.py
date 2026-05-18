from umutextstats.config.models import DimensionConfig, UMUTextStatsConfig
from umutextstats.config.tree import render_config_tree


def test_render_config_tree():
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
                            ),
                            DimensionConfig(
                                key="morphosyntax-gender-masculine",
                            ),
                        ],
                    ),
                    DimensionConfig(
                        key="morphosyntax-number",
                    ),
                ],
            )
        ]
    )

    assert render_config_tree(config) == "\n".join(
        [
            "└── morphosyntax",
            "    ├── morphosyntax-gender",
            "    │   ├── morphosyntax-gender-feminine",
            "    │   └── morphosyntax-gender-masculine",
            "    └── morphosyntax-number",
        ]
    )


def test_render_config_tree_max_depth():
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
                            ),
                        ],
                    ),
                ],
            )
        ]
    )

    assert render_config_tree(config, max_depth=1) == "\n".join(
        [
            "└── morphosyntax",
            "    └── morphosyntax-gender",
        ]
    )