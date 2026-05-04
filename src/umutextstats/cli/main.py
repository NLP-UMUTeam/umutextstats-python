# src/umutextstats/cli/main.py

import argparse

from umutextstats.cache import CacheManager
from umutextstats.config import load_config
from umutextstats.dimensions import DimensionEngine
from umutextstats.io import read_input
from umutextstats.nlp import annotate_dataframe_with_stanza
from umutextstats.output import write_output
from umutextstats.preprocessing.pipeline import preprocess_dataframe_cached
from umutextstats.utils.profiler import Profiler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="umutextstats",
        description="UMUTextStats linguistic feature extraction tool",
    )

    parser.add_argument(
        "input",
        help="Input CSV file",
    )

    parser.add_argument(
        "-t",
        "--text-column",
        required=True,
        help="Name of the column containing the input text",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="features.csv",
        help="Output file path. Supported: .csv, .json",
    )

    parser.add_argument(
        "-c",
        "--config",
        default=None,
        help="XML configuration file. If omitted, package default.xml is used.",
    )

    parser.add_argument(
        "--cache-dir",
        default=".cache",
        help="Cache directory",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable stage cache",
    )

    parser.add_argument(
        "--no-stanza",
        action="store_true",
        help="Skip Stanza POS/NER annotation",
    )

    parser.add_argument(
        "--stats",
        default=None,
        help="Optional path to save profiling stats. Supported: .csv, .json",
    )

    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bars",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    use_cache = not args.no_cache
    show_progress = not args.no_progress

    cache = CacheManager(args.cache_dir)
    profiler = Profiler(enabled=args.stats is not None)

    with profiler.track("config", "load_config"):
        config = load_config(args.config)

    with profiler.track("io", "read_input"):
        df = read_input(args.input, text_column=args.text_column)

    with profiler.track("preprocessing", "normalize"):
        df = preprocess_dataframe_cached(
            df,
            input_path=args.input,
            cache=cache,
            use_cache=use_cache,
            show_progress=show_progress,
        )

    if not args.no_stanza:
        with profiler.track("nlp", "stanza"):
            df = annotate_dataframe_with_stanza(
                df,
                input_path=args.input, 
                cache=cache,
                use_cache=use_cache,
            )

    engine = DimensionEngine(
        config=config,
        input_column="text_norm",
        include_unimplemented=True,
        profiler=profiler,
        show_progress=show_progress,
    )

    with profiler.track("dimensions", "compute"):
        features = engine.compute(df)

    with profiler.track("output", "write_features"):
        write_output(features, args.output)

    if args.stats:
        write_output(profiler.dataframe(), args.stats)


if __name__ == "__main__":
    main()