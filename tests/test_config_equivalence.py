import argparse

import pandas as pd

from umutextstats.cli.analyze import run_analyze


XML_CONFIG = "src/umutextstats/resources/config/default.xml"
YAML_CONFIG = "src/umutextstats/resources/config/default.yaml"


def run_analyze_with_config(input_path, output_path, config_path):
    args = argparse.Namespace(
        input=str(input_path),
        text_column="text",
        output=str(output_path),
        head=None,
        config=str(config_path),
        only="phonetics|stylometry-corpus-words-count|stylometry-corpus-length",
        cache_dir=str(input_path.parent / ".cache"),
        no_cache=True,
        no_stanza=True,
        stats=None,
        no_progress=True,
    )

    run_analyze(args)


def test_yaml_and_xml_produce_same_cli_output(tmp_path):
    input_path = tmp_path / "input.csv"
    xml_output_path = tmp_path / "xml_features.csv"
    yaml_output_path = tmp_path / "yaml_features.csv"

    pd.DataFrame(
        {
            "text": [
                "Hola hola hola!!!",
                "Esto es una prueba.",
                "Soooooy un texto con alargamiento.",
            ]
        }
    ).to_csv(input_path, index=False)

    run_analyze_with_config(input_path, xml_output_path, XML_CONFIG)
    run_analyze_with_config(input_path, yaml_output_path, YAML_CONFIG)

    xml_features = pd.read_csv(xml_output_path)
    yaml_features = pd.read_csv(yaml_output_path)

    pd.testing.assert_frame_equal(
        xml_features,
        yaml_features,
        check_dtype=False,
    )