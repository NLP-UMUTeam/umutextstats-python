# compare_csv_columns.py

import sys
import pandas as pd


OLD_PATH = "economy-lf.csv"
NEW_PATH = "economy-lf-2.csv"


def main():
    old = pd.read_csv(OLD_PATH)
    new = pd.read_csv(NEW_PATH)

    print(f"Old shape: {old.shape}")
    print(f"New shape: {new.shape}")
    print()

    old_cols = set(old.columns)
    new_cols = set(new.columns)

    only_old = sorted(old_cols - new_cols)
    only_new = sorted(new_cols - old_cols)
    common = [col for col in old.columns if col in new_cols]

    if only_old:
        print("Columns only in old:")
        for col in only_old:
            print(f"  - {col}")
        print()

    if only_new:
        print("Columns only in new:")
        for col in only_new:
            print(f"  - {col}")
        print()

    print("Columns with different values:")

    found = False

    for col in common:
        left = old[col]
        right = new[col]

        if len(left) != len(right):
            print(f"  - {col}: different row count")
            found = True
            continue

        left_cmp = left.fillna("__NA__")
        right_cmp = right.fillna("__NA__")

        diff_mask = left_cmp.ne(right_cmp)

        if diff_mask.any():
            found = True
            diff_count = int(diff_mask.sum())
            total = len(diff_mask)

            print(f"  - {col}: {diff_count}/{total} rows differ")

    if not found:
        print("  No differences in common columns.")


if __name__ == "__main__":
    main()