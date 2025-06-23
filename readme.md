# TextKGCData: Textual Knowledge Graph Data Toolkit

TextKGCData is a Python toolkit for downloading, processing, standardizing, and loading knowledge graph data with rich textual descriptions. It provides a powerful CLI and Python API for preparing datasets like WN18RR and Wikidata5M for use in text-based knowledge graph completion and related tasks. The full documentation is available at [text-kgc-data-docs](https://tj-coding.github.io/TextKGCData/).


---

## Features
- **Download**: Fetches datasets from the SimKGC repository.
- **Standardize**: Converts raw entity and relation files into clean, model-ready formats.
- **Preprocess**: Fills missing entries, truncates descriptions, and ensures data consistency.
- **Load**: Easily load processed data into your Python projects.

---
## Add to Your Project
`git submodule add https://github.com/TJ-coding/TextKGCData.git packages`

## Installation
`pip install git+https://github.com/TJ-coding/TextKGCData.git@branch#subdirectory=text_kgc_data_proj`

## Quickstart

### 1. Download a dataset

```shell
tkg download-text-kgc-dataset --data-dir-name WN18RR
```

### 2. Standardize and preprocess

See the [WN18RR tutorial](text-kgc-data-docs/docs/wn18rr_example.md) and [Wikidata5M tutorial](text-kgc-data-docs/docs/wikidata5m_example.md) for full workflows.

---

## CLI Overview

All commands are available via the CLI:

```shell
tkg [COMMAND] [OPTIONS]
```

Key commands:
- `download-text-kgc-dataset` — Download datasets
- `standardize-wn18rr-entity-files-cli` — Standardize WN18RR entity files
- `standardize-wn18rr-relation-file-cli` — Standardize WN18RR relation file
- `standardize-wikidata5m-entity-files-cli` — Standardize Wikidata5M entity files
- `standardize-wikidata5m-relation-file-cli` — Standardize Wikidata5M relation file
- `fill-missing-entries-cli` — Fill missing names/descriptions
- `truncate-description-cli` — Truncate descriptions for model compatibility

Run `tkg --help` for all options.

---

## Project Structure

```
text_kgc_data/
    cli.py              # Command line interface
    download_data.py    # Downloading data from SimKGC Repo
    helpers.py          # Helper functions
    preprocessors.py    # Data cleaning utilities
    standardise_tkg_files/
       standardise_wn18rr.py      # WN18RR standardization
       standardise_wikidata5m.py  # Wikidata5M standardization

text-kgc-data-docs/
    mkdocs.yml    # MkDocs config
    docs/
        index.md  # Main documentation
        wn18rr_example.md  # WN18RR tutorial
        wikidata5m_example.md  # Wikidata5M tutorial
```

---

## Documentation

- Full documentation and tutorials: [docs/index.md](text-kgc-data-docs/docs/index.md)
- WN18RR example: [docs/wn18rr_example.md](text-kgc-data-docs/docs/wn18rr_example.md)
- Wikidata5M example: [docs/wikidata5m_example.md](text-kgc-data-docs/docs/wikidata5m_example.md)

---

## License
MIT
