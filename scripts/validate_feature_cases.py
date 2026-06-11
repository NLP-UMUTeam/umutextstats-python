from pathlib import Path

import argparse
import pandas as pd
import yaml

from rich.console import Console
from rich.table import Table

from umutextstats.config.inspect import inspect_dimension_text
from umutextstats.config.loader import load_config
from umutextstats.dimensions.factory import build_runtime_dimension
from umutextstats.io.text import ensure_text


console = Console()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        default=None,
        help="Validate only dimensions whose key starts with this prefix.",
    )
    return parser.parse_args()


def default_cases_path_for_key(key: str) -> Path:
    filename = key.replace("-", "_") + ".yaml"
    return Path("tests/feature_cases") / filename


def iter_dimensions(dimensions, root: Path):
    for dimension in dimensions:
        validation = getattr(dimension, "validation", None) or {}

        explicit_cases_path = validation.get("cases")
        default_cases_path = default_cases_path_for_key(dimension.key)

        if explicit_cases_path:
            yield dimension, Path(explicit_cases_path), "explicit"
        elif (root / default_cases_path).exists():
            yield dimension, default_cases_path, "convention"
        else:
            yield dimension, default_cases_path, "missing"

        yield from iter_dimensions(dimension.children, root)


def build_case_row(case):
    """
    Build a single-row runtime context for a feature case.

    The row mirrors the DataFrame columns used by dimensions:
    raw text, normalized text, and any annotation columns.
    """
    text = ensure_text(case.get("text", ""))
    annotations = case.get("annotations") or {}

    return {
        "text": text,
        "text_raw": text,
        "text_norm": text,
        **annotations,
    }


def compute_dimension_case(dimension, row):
    runtime_dimension = build_runtime_dimension(dimension)

    if runtime_dimension is None:
        raise ValueError(
            f"Could not build runtime dimension: {dimension.key}"
        )

    df = pd.DataFrame([row])
    result = runtime_dimension.compute(df)

    return result.iloc[0] if hasattr(result, "iloc") else result[0]


def print_stats_table(stats):
    if not stats:
        return

    table = Table(title="Feature Validation Summary")

    table.add_column("Dimension", style="cyan")
    table.add_column("Cases", justify="right")
    table.add_column("Passed", justify="right", style="green")
    table.add_column("Failed", justify="right", style="red")
    table.add_column("File", style="dim")

    for row in stats:
        table.add_row(
            row["dimension"],
            str(row["cases"]),
            str(row["passed"]),
            str(row["failed"]),
            row["file"],
        )

    console.print()
    console.print(table)


def load_cases(full_cases_path: Path) -> list[dict]:
    data = yaml.safe_load(
        full_cases_path.read_text(encoding="utf-8")
    ) or {}

    return data.get("cases", [])


def inspect_failed_case(config, dimension, case, row):
    text = ensure_text(case.get("text", ""))
    annotations = case.get("annotations") or {}

    return inspect_dimension_text(
        config=config,
        key=dimension.key,
        text=text,
        annotations=annotations,
    )


def main():
    args = parse_args()

    config = load_config()
    root = Path(__file__).parent.parent

    total_dimensions = 0
    covered_dimensions = 0
    total_cases = 0
    failures = []
    stats = []

    for dimension, cases_path, source in iter_dimensions(
        config.dimensions,
        root,
    ):
        if args.only and not dimension.key.startswith(args.only):
            continue

        if dimension.children:
            continue

        total_dimensions += 1

        full_cases_path = root / cases_path
        passed = 0
        failed = 0

        if not full_cases_path.exists():
            if source != "missing":
                failed += 1
                failures.append(
                    f"{dimension.key}: cases file does not exist: "
                    f"{full_cases_path}"
                )
                stats.append(
                    {
                        "dimension": dimension.key,
                        "file": str(cases_path),
                        "cases": 0,
                        "passed": passed,
                        "failed": failed,
                    }
                )

            continue

        covered_dimensions += 1
        cases = load_cases(full_cases_path)

        if not cases:
            failed += 1
            failures.append(
                f"{dimension.key}: no cases found in {full_cases_path}"
            )
            stats.append(
                {
                    "dimension": dimension.key,
                    "file": str(cases_path),
                    "cases": 0,
                    "passed": passed,
                    "failed": failed,
                }
            )
            continue

        for i, case in enumerate(cases):
            total_cases += 1
            case_failed = False

            row = build_case_row(case)
            value = compute_dimension_case(dimension, row)

            if "expected_min" in case and case["expected_min"] <= 0:
                failures.append(
                    f"{dimension.key}[{i}]: expected_min must be > 0. "
                    f"Use expected: 0 for negatives."
                )
                case_failed = True

            if "expected" in case and value != case["expected"]:
                case_failed = True

            if "expected_min" in case and value < case["expected_min"]:
                case_failed = True

            if case_failed:
                inspection = inspect_failed_case(
                    config=config,
                    dimension=dimension,
                    case=case,
                    row=row,
                )

                failures.append(
                    f"{dimension.key}[{i}]: expected "
                    f"{case.get('expected', case.get('expected_min'))}, "
                    f"got {value}. Text: {case.get('text', '')!r}. "
                    f"Matches: {[m.match for m in inspection.matches]}. "
                    f"Discarded: "
                    f"{[m.match for m in inspection.discarded_matches]}"
                )

                failed += 1
            else:
                passed += 1

        stats.append(
            {
                "dimension": dimension.key,
                "file": str(cases_path),
                "cases": len(cases),
                "passed": passed,
                "failed": failed,
            }
        )

    print(f"Validated feature cases: {total_cases}")
    print_stats_table(stats)

    coverage = (
        covered_dimensions / total_dimensions
        if total_dimensions
        else 0.0
    )

    print(
        f"Covered dimensions: {covered_dimensions} / "
        f"{total_dimensions} ({coverage:.1%})"
    )

    if failures:
        print("")
        print("Failures:")

        for failure in failures:
            print(f"- {failure}")

        raise SystemExit(1)

    print("")
    print("All feature cases passed.")


if __name__ == "__main__":
    main()