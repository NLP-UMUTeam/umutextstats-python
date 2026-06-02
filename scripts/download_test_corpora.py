from pathlib import Path
from urllib.request import Request, urlopen

from tqdm.auto import tqdm


CORPORA_DIR = Path("tests/corpora")
RAW_DIR = CORPORA_DIR / "raw"
CLEAN_DIR = CORPORA_DIR / "clean"

CHUNK_SIZE = 1024 * 1024

TEXTS = {
    "don_quijote.txt": "https://www.gutenberg.org/cache/epub/2000/pg2000.txt"
}


def unwrap_hard_wrapped_lines(text: str) -> str:
    """
    Convert hard-wrapped lines into normal paragraphs.

    Keeps paragraph boundaries, represented by blank lines.
    """
    output: list[str] = []
    current_paragraph: list[str] = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            if current_paragraph:
                output.append(" ".join(current_paragraph))
                current_paragraph = []
            continue

        current_paragraph.append(line)

    if current_paragraph:
        output.append(" ".join(current_paragraph))

    return "\n\n".join(output) + "\n"


def download_text(url: str, output_path: Path) -> None:
    request = Request(
        url,
        headers={"User-Agent": "UMUTextStats test corpus downloader"},
    )

    with urlopen(request, timeout=60) as response:
        total = response.headers.get("Content-Length")
        total_size = int(total) if total is not None else None

        with output_path.open("wb") as file:
            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=output_path.name,
            ) as progress:
                while True:
                    chunk = response.read(CHUNK_SIZE)

                    if not chunk:
                        break

                    file.write(chunk)
                    progress.update(len(chunk))


def clean_text_file(raw_path: Path, clean_path: Path) -> None:
    text = raw_path.read_text(encoding="utf-8", errors="replace")
    clean_text = unwrap_hard_wrapped_lines(text)
    clean_path.write_text(clean_text, encoding="utf-8")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in TEXTS.items():
        raw_path = RAW_DIR / filename
        clean_path = CLEAN_DIR / filename

        if not raw_path.exists():
            print(f"Downloading {url}")
            download_text(url, raw_path)
        else:
            print(f"Skipping existing raw file: {raw_path}")

        print(f"Cleaning {raw_path}")
        clean_text_file(raw_path, clean_path)
        print(f"Saved clean file: {clean_path}")


if __name__ == "__main__":
    main()