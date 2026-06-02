import sys

import pandas as pd

from umutextstats.io.text import ensure_text


class StdinInputResolver:
    def supports(self, path):
        return str(path) == "-"

    def read(self, path, text_column: str):
        content = sys.stdin.read()

        try:
            from io import StringIO

            df = pd.read_csv(StringIO(content))

            if text_column in df.columns:
                df = df.copy()

                df["text_raw"] = df[text_column].map(ensure_text)
                df["text"] = df["text_raw"]

                if "id" not in df.columns:
                    df.insert(0, "id", range(len(df)))

                return df

        except Exception:
            pass

        return pd.DataFrame(
            {
                "id": [0],
                "text_raw": [ensure_text(content)],
                "text": [ensure_text(content)],
            }
        )