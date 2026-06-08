import unicodedata
from collections import defaultdict
from pathlib import Path

import regex as re


ACCENTED = set("áéíóúüÁÉÍÓÚÜ")


def remove_accents(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    return "".join(
        ch for ch in text
        if unicodedata.category(ch) != "Mn"
    )


def has_accent(word: str) -> bool:
    return any(ch in ACCENTED for ch in word)


def is_literal_text(text: str) -> bool:
    return bool(re.fullmatch(r"\p{L}+(?:\s+\p{L}+)*", text))


def iter_words_from_line(line: str):
    line = line.strip().lower()

    if not line or line.startswith("#"):
        return

    if not is_literal_text(line):
        return

    for word in line.split():
        if word:
            yield word


def main():
    dictionary_dir = Path("src/umutextstats/resources/dictionaries")

    sources = [
        dictionary_dir / "es.txt",
        *dictionary_dir.glob("verbs-*.txt"),
    ]

    output = Path("src/umutextstats/resources/accent_maps/es.txt")
    ambiguous_output = Path(
        "src/umutextstats/resources/accent_maps/es_ambiguous.txt"
    )

    groups = defaultdict(set)
    unaccented_words = set()

    for source in sources:
        if not source.exists():
            continue

        for raw_line in source.read_text(encoding="utf-8").splitlines():
            for word in iter_words_from_line(raw_line):
                plain = remove_accents(word)

                if plain == word:
                    unaccented_words.add(word)
                    continue

                groups[plain].add(word)

    clean = {}
    ambiguous = {}

    for plain, accented_forms in groups.items():
        if plain in unaccented_words:
            ambiguous[plain] = sorted(accented_forms)
            continue

        if len(accented_forms) == 1:
            clean[plain] = next(iter(accented_forms))
        else:
            ambiguous[plain] = sorted(accented_forms)

    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        "\n".join(sorted(clean.values())) + "\n",
        encoding="utf-8",
    )

    ambiguous_output.write_text(
        "\n".join(
            f"{plain}\t{','.join(forms)}"
            for plain, forms in sorted(ambiguous.items())
        ) + "\n",
        encoding="utf-8",
    )

    print(f"sources: {len(sources)}")
    print(f"clean: {len(clean)}")
    print(f"ambiguous: {len(ambiguous)}")


if __name__ == "__main__":
    main()