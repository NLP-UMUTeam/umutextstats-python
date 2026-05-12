import sys

import pandas as pd


class StdinInputResolver:
    def supports(self, path):
        return str(path) == "-"

    def read(self, path, text_column: str):
        df = pd.read_csv(sys.stdin)
        
        if text_column not in df.columns:
            raise ValueError(f"Text column '{text_column}' not found in CSV from stdin")

        df = df.copy()

        df["text_raw"] = df[text_column].fillna("").astype(str)
        df["text"] = df["text_raw"]

        if "id" not in df.columns:
            df.insert(0, "id", range(len(df)))

        return df