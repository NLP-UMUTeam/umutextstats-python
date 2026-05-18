# src/umutextstats/config/convert.py

from pathlib import Path

from umutextstats.config.loader import load_config
from umutextstats.config.yaml_exporter import save_yaml_config


def convert_config(input_path: str | Path, output_path: str | Path) -> None:
    input_path = Path(input_path)
    output_path = Path(output_path)

    config = load_config(input_path)

    if output_path.suffix not in {".yaml", ".yml"}:
        raise ValueError(f"Unsupported output format: {output_path.suffix}")

    save_yaml_config(config, output_path) 