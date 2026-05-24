from __future__ import annotations
from pathlib import Path

import argparse
import time
import pandas as pd

from umutextstats.cache import CacheManager
from umutextstats.cli.cache import run_cache


def make_args(**kwargs):
    defaults = {
        "cache_command": None,
        "cache_dir": None,
        "yes": True,
        "limit": 50,
        "older_than_days": 30,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cache_cli_info(tmp_path, capsys):
    cache = CacheManager(tmp_path)
    cache.save(pd.DataFrame({"a": [1, 2, 3]}), "stage", "key1")

    args = make_args(
        cache_command="info",
        cache_dir=str(tmp_path),
    )

    run_cache(args)

    captured = capsys.readouterr()

    assert "Cache dir:" in captured.out
    assert "Exists: True" in captured.out
    assert "Files:" in captured.out
    assert "Size:" in captured.out


def test_cache_cli_list(tmp_path, capsys):
    cache = CacheManager(tmp_path)
    cache.save(pd.DataFrame({"a": [1]}), "stage", "key1")

    args = make_args(
        cache_command="list",
        cache_dir=str(tmp_path),
        limit=10,
    )

    run_cache(args)

    captured = capsys.readouterr()

    assert "stage" in captured.out
    assert "key1" in captured.out


def test_cache_cli_clear(tmp_path):
    cache = CacheManager(tmp_path)
    cache.save(pd.DataFrame({"a": [1]}), "stage", "key1")

    assert tmp_path.exists()
    assert any(tmp_path.rglob("*"))

    args = make_args(
        cache_command="clear",
        cache_dir=str(tmp_path),
        yes=True,
    )

    run_cache(args)

    assert not tmp_path.exists()


def test_cache_cli_prune(tmp_path):
    cache = CacheManager(tmp_path)
    cache.save(pd.DataFrame({"a": [1]}), "stage", "old_key")

    files = [path for path in tmp_path.rglob("*") if path.is_file()]
    assert files

    old_time = time.time() - 60 * 60 * 24 * 40

    for path in files:
        path.touch()
        path.chmod(0o644)
        import os

        os.utime(path, (old_time, old_time))

    args = make_args(
        cache_command="prune",
        cache_dir=str(tmp_path),
        older_than_days=30,
        yes=True,
    )

    run_cache(args)

    remaining_files = [path for path in tmp_path.rglob("*") if path.is_file()]
    assert remaining_files == []
    
    
from umutextstats.cli.analyze import resolve_cache_policy


def test_cache_policy_normal_run_reads_and_writes():
    assert resolve_cache_policy(
        use_cache=True,
        is_stdin=False,
        head=None,
        only=None,
    ) == (True, True)


def test_cache_policy_head_reads_but_does_not_write():
    assert resolve_cache_policy(
        use_cache=True,
        is_stdin=False,
        head=5,
        only=None,
    ) == (True, False)


def test_cache_policy_only_reads_but_does_not_write():
    assert resolve_cache_policy(
        use_cache=True,
        is_stdin=False,
        head=None,
        only="stylometry",
    ) == (True, False)


def test_cache_policy_stdin_disables_cache():
    assert resolve_cache_policy(
        use_cache=True,
        is_stdin=True,
        head=None,
        only=None,
    ) == (False, False)


def test_cache_policy_no_cache_disables_cache():
    assert resolve_cache_policy(
        use_cache=False,
        is_stdin=False,
        head=None,
        only=None,
    ) == (False, False)
    
    
def test_cache_keys_include_head(tmp_path):
    cache = CacheManager(tmp_path)

    params_full = {
        "input_column": "text_norm",
        "cache_version": 1,
        "head": None,
    }

    params_head = {
        "input_column": "text_norm",
        "cache_version": 1,
        "head": 5,
    }
    
    

    key_full = cache.build_key(Path(__file__).parent / "fixtures" / "sample.csv", "common_features", params_full)
    key_head = cache.build_key(Path(__file__).parent / "fixtures" / "sample.csv", "common_features", params_head)

    assert key_full != key_head
    
    
def resolve_cache_policy(
    use_cache: bool,
    is_stdin: bool,
    head: int | None,
    only: str | None,
):
    use_cache = use_cache and not is_stdin
    read_cache = use_cache
    write_cache = use_cache and head is None and only is None

    return read_cache, write_cache