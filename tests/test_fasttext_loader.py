# tests/test_fasttext_loader.py

import sys
import types

from umutextstats.utils.fasttext_loader import FastTextLoader


class FakeFastTextModule:
    @staticmethod
    def load_model(path):
        return {"model_path": path}


def test_fasttext_loader_uses_existing_model(tmp_path, monkeypatch):
    FastTextLoader._model = None

    model_dir = tmp_path / "fasttext"
    model_dir.mkdir()
    model_path = model_dir / "lid.176.ftz"
    model_path.write_text("fake model")

    monkeypatch.setitem(sys.modules, "fasttext", FakeFastTextModule)

    model = FastTextLoader.get_model(cache_dir=model_dir)

    assert model["model_path"] == str(model_path)


def test_fasttext_loader_downloads_if_missing(tmp_path, monkeypatch):
    FastTextLoader._model = None

    model_dir = tmp_path / "fasttext"

    def fake_urlretrieve(url, path):
        path.write_text("fake downloaded model")

    monkeypatch.setitem(sys.modules, "fasttext", FakeFastTextModule)
    monkeypatch.setattr(
        "urllib.request.urlretrieve",
        fake_urlretrieve,
    )

    model = FastTextLoader.get_model(cache_dir=model_dir)

    assert model["model_path"].endswith("lid.176.ftz")
    assert (model_dir / "lid.176.ftz").exists()


def test_fasttext_loader_caches_model(tmp_path, monkeypatch):
    FastTextLoader._model = None

    model_dir = tmp_path / "fasttext"
    model_dir.mkdir()
    (model_dir / "lid.176.ftz").write_text("fake model")

    calls = {"count": 0}

    class CountingFastTextModule:
        @staticmethod
        def load_model(path):
            calls["count"] += 1
            return {"model_path": path} 

    monkeypatch.setitem(sys.modules, "fasttext", CountingFastTextModule)

    model1 = FastTextLoader.get_model(cache_dir=model_dir)
    model2 = FastTextLoader.get_model(cache_dir=model_dir)

    assert model1 is model2
    assert calls["count"] == 1


def test_fasttext_loader_returns_none_if_fasttext_missing(monkeypatch):
    FastTextLoader._model = None

    monkeypatch.setitem(sys.modules, "fasttext", None)

    model = FastTextLoader.get_model()

    assert model is None