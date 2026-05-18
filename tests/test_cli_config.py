from umutextstats.cli.main import build_parser


def test_config_convert_xml_to_yaml(tmp_path):
    input_path = tmp_path / "config.xml"
    output_path = tmp_path / "config.yaml"

    input_path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <directory_folder>es</directory_folder>
    <dimensions>
        <dimension>
            <key>phonetics</key>
            <class>CompositeDimension</class>
            <strategy>CompositeStrategySum</strategy>
            <dimensions>
                <dimension>
                    <key>phonetics-expressive-lengthening</key>
                    <class>PatternDimension</class>
                    <pattern>(.)\\1{3,}</pattern>
                    <useoriginalinput>true</useoriginalinput>
                </dimension>
            </dimensions>
        </dimension>
    </dimensions>
</configuration>
""",
        encoding="utf-8",
    )

    parser = build_parser()
    args = parser.parse_args(
        [
            "config",
            "convert",
            str(input_path),
            str(output_path),
        ]
    )
    args.func(args)

    assert output_path.exists()

    yaml_text = output_path.read_text(encoding="utf-8")
    assert "directory_folder: es" in yaml_text
    assert "key: phonetics" in yaml_text
    assert "key: phonetics-expressive-lengthening" in yaml_text
    assert "use_original_input: true" in yaml_text