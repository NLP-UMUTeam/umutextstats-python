from __future__ import annotations

import argparse
import pandas as pd
from rich.console import Console
from pathlib import Path

from umutextstats.cli.command import CommandSpec
from umutextstats.config import load_config
from umutextstats.config.inspect import (
    inspect_dimension_text,
    render_inspection,
)

from umutextstats.nlp.stanza_annotator import (
    StanzaAnnotator,
    format_tagged_pos,
    format_tagged_dep,
    format_tagged_ner,
    format_tagged_morph,
)


def add_inspect_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "key",
        help="Dimension key to inspect.",
    )

    parser.add_argument(
        "input",
        help="Input text file or '-' for stdin.",
    )

    parser.add_argument(
        "-c",
        "--config",
        default=None,
        help="Configuration file. If omitted, package default config is used.",
    )

    parser.add_argument(
        "--annotate",
        action="store_true",
        help="Run linguistic annotation before inspection.",
    )

def run_inspect(args: argparse.Namespace) -> None:
    config = load_config(args.config)

    if args.input == "-":
        import sys
        text = sys.stdin.read()
    else:
        text = Path(args.input).read_text(encoding="utf-8")

    annotations = None

    if args.annotate:
        annotator = StanzaAnnotator()
        docs = annotator.annotate_texts([text])
        doc = docs[0]

        annotations = {
            "tagged_pos": format_tagged_pos(doc),
            "tagged_dep": format_tagged_dep(doc),
            "tagged_ner": format_tagged_ner(doc),
            "tagged_morph": format_tagged_morph(doc),
        }

    inspection = inspect_dimension_text(
        config=config,
        key=args.key,
        text=text,
        annotations=annotations,
    )

    console = Console()
    console.print(render_inspection(inspection, text))
    

COMMAND = CommandSpec(
    name="inspect",
    help="Inspect a dimension",
    add_arguments=add_inspect_arguments,
    run=run_inspect,
)