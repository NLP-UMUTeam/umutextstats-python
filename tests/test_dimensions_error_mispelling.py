import pandas as pd
import pytest

from umutextstats.dimensions.error import ErrorMispellingDimension


def hunspell_available():
    try:
        from spylls.hunspell import Dictionary

        Dictionary.from_files(
            "/usr/share/hunspell/es_ES"
        )
        return True

    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not hunspell_available(),
    reason="Hunspell Spanish dictionary not available",
)