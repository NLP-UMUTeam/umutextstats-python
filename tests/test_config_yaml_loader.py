# tests/test_config_yaml_loader.py

from pathlib import Path

from umutextstats.config.yaml_loader import load_yaml_config


def test_load_yaml_config(tmp_path: Path):
    path = tmp_path / "config.yaml"
    path.write_text(
        """
directory_folder: es
dimensions:
  - key: phonetics
    class: CompositeDimension
    strategy: CompositeStrategySum
    children:
      - key: phonetics-expressive-lengthening
        class: PatternDimension
        pattern: '(.)\\1{3,}'
        use_original_input: true
""",
        encoding="utf-8",
    )

    config = load_yaml_config(path)

    assert config.directory_folder == "es"
    assert config.dimensions[0].key == "phonetics"
    assert config.dimensions[0].children[0].key == "phonetics-expressive-lengthening"
    assert config.dimensions[0].children[0].class_name == "PatternDimension"
    assert config.dimensions[0].children[0].use_original_input is True