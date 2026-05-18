# tests/test_config_yaml_exporter.py

from umutextstats.config.models import DimensionConfig, UMUTextStatsConfig
from umutextstats.config.yaml_exporter import dump_yaml_config


def test_dump_yaml_config():
    config = UMUTextStatsConfig(
        directory_folder="es",
        dimensions=[
            DimensionConfig(
                key="phonetics",
                class_name="CompositeDimension",
                strategy="CompositeStrategySum",
                children=[
                    DimensionConfig(
                        key="phonetics-expressive-lengthening",
                        class_name="PatternDimension",
                        pattern=r"(.)\1{3,}",
                        use_original_input=True,
                    )
                ],
            )
        ],
    )

    yaml_text = dump_yaml_config(config)

    assert "directory_folder: es" in yaml_text
    assert "key: phonetics" in yaml_text
    assert "class: CompositeDimension" in yaml_text
    assert "key: phonetics-expressive-lengthening" in yaml_text
    assert "use_original_input: true" in yaml_text