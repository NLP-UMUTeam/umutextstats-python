import os
import urllib.request
from pathlib import Path

_MODEL_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz"
_MODEL_NAME = "lid.176.ftz"


class FastTextLoader:
    _model = None

    @classmethod
    def get_model(cls, cache_dir=".cache/fasttext"):
        if cls._model is not None:
            return cls._model

        try:
            import fasttext
        except ImportError:
            return None

        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)

        model_path = cache_path / _MODEL_NAME

        if not model_path.exists():
            urllib.request.urlretrieve(_MODEL_URL, model_path)

        cls._model = fasttext.load_model(str(model_path))

        return cls._model