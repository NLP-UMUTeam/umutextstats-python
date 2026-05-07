<p align="center">
  <img src="docs/umutextstats-logo.png" alt="UMUTextStats logo" width="500"/>
</p>

# UMUTextStats Python

Work in progress Python port of **UMUTextStats**, a linguistic feature extraction framework inspired by LIWC and stylometric analysis systems.

The project analyzes text datasets and extracts lexical, morphosyntactic, stylistic, pragmatic, psycholinguistic, social-media and error-related features from an XML configuration file.

---

# Status

This is an active migration/adaptation of UMUTextStats to Python.

Current features include:

- CSV input loading
- XML configuration loading
- Text preprocessing
- Cached pipeline stages
- Common feature computation
- Stanza POS/NER annotation
- Dictionary-based dimensions
- Pattern-based dimensions
- Composite dimensions
- Feature summarization
- Feature ranking
- Sparse/zero-only feature detection
- Aggregate statistics by metadata groups
- CSV/JSON output
- Optional profiling stats

---

# Installation

```bash
pip install -e .
```

---

# CLI Usage

## Analyze

Extract linguistic features from a dataset.

```bash
umutextstats analyze dataset.csv -t tweet -o features.csv
```

With profiling stats:

```bash
umutextstats analyze dataset.csv \
  -t tweet \
  -o features.csv \
  --stats stats.csv
```

Using a custom XML configuration:

```bash
umutextstats analyze dataset.csv \
  -t tweet \
  -c path/to/config.xml \
  -o features.csv
```

Disable cache:

```bash
umutextstats analyze dataset.csv \
  -t tweet \
  -o features.csv \
  --no-cache
```

---

## Summarize

Compute descriptive statistics from extracted features.

```bash
umutextstats summarize features.csv
```

Generate JSON summary:

```bash
umutextstats summarize features.csv \
  -o summary.json
```

Force long/tidy CSV format:

```bash
umutextstats summarize features.csv \
  --format long \
  -o summary.csv
```

Force nested JSON format:

```bash
umutextstats summarize features.csv \
  --format nested \
  -o summary.json
```

---

## Aggregate

Compute grouped statistics using metadata columns.

Example dataset:

| id | text | split | author |
|---|---|---|---|
| 1 | ... | train | alice |
| 2 | ... | test | bob |

Example features:

| id | feature_1 | feature_2 |
|---|---|---|
| 1 | ... | ... |
| 2 | ... | ... |

Aggregate by split:

```bash
umutextstats aggregate \
  features.csv \
  --metadata dataset.csv \
  --group-by split \
  --id-column id \
  -o aggregate_by_split.json
```

Aggregate by author:

```bash
umutextstats aggregate \
  features.csv \
  --metadata dataset.csv \
  --group-by author \
  --id-column id \
  -o aggregate_by_author.json
```

---

# Output Formats

Supported output formats:

```text
.csv
.json
```

Outputs include:

- Feature matrices
- Dataset summaries
- Feature rankings
- Aggregate/group statistics

---

# Cache

By default, intermediate stages are cached in:

```text
.cache/
```

Cached stages include:

- Preprocessing
- Common computed features
- Stanza annotations

Each stage stores only its own generated columns to avoid overwriting intermediate pipeline data.

---

# Feature Analysis

UMUTextStats includes utilities for:

- Descriptive statistics
- Feature ranking
- Sparse feature detection
- Zero-only feature detection

Future analysis modules may include:

- Mutual Information
- Information Gain
- Effect Size
- Discriminative feature analysis
- Stylometric profiling

---

# Development

Run tests with:

```bash
pytest
```

---

# Notes

This project is still under development.

Results, APIs and internal feature implementations may change while the Python version is being aligned with the original UMUTextStats behavior.