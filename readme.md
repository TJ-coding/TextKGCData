# TextKGCData: Functional Text Knowledge Graph Toolkit

A simple, functional toolkit for downloading, processing, and working with knowledge graph datasets for text-based knowledge graph completion. Follows Unix philosophy with composable functions that do one thing well.

## Features

- **Functional Design**: Pure functions with clear inputs/outputs  
- **Unix Philosophy**: Small, composable tools that can be chained together
- **Type Safety**: Full Beartype validation for runtime type checking
- **Clear Naming**: Function names describe exactly what they create (`create_entity_id2name_wn18rr`)
- **Dataset Support**: WN18RR and Wikidata5M datasets
- **CLI + Programmatic**: Use via command line or import as Python library

## Installation

```bash
pip install git+https://github.com/TJ-coding/TextKGCData.git@branch#subdirectory=text_kgc_data_proj
```

## Quick Start

### CLI Usage

```bash
# Download WN18RR dataset
text-kgc wn18rr download ./data

# Create entity mappings
text-kgc wn18rr create-entity-mappings ./data/WN18RR/wordnet-mlj12-definitions.txt ./output

# Create relation mappings  
text-kgc wn18rr create-relation-mappings ./data/WN18RR/relations.dict ./output

# Run complete pipeline
text-kgc wn18rr process-pipeline ./data/WN18RR ./output --fill-missing --truncate-descriptions --tokenizer-name bert-base-uncased

# Fill missing entries
text-kgc fill-missing-entries ./output/entity_id2name.json ./output/entity_id2description.json ./filled

# Truncate descriptions
text-kgc truncate-descriptions ./output/entity_id2description.json bert-base-uncased ./truncated
```

### Programmatic Usage

```python
from pathlib import Path
from text_kgc_data.datasets.wn18rr import (
    download_wn18rr,
    create_entity_id2name_wn18rr,
    create_entity_id2description_wn18rr,
    create_relation_id2name_wn18rr
)
from text_kgc_data.processors import fill_missing_entity_entries
from text_kgc_data.io import save_json

# Download data
data_path = download_wn18rr(Path("./data"))

# Create mappings
definitions_file = data_path / "wordnet-mlj12-definitions.txt"
entity_names = create_entity_id2name_wn18rr(definitions_file)
entity_descriptions = create_entity_id2description_wn18rr(definitions_file)

# Process data
filled_names, filled_descriptions = fill_missing_entity_entries(
    entity_names, entity_descriptions
)

# Save results
save_json(filled_names, Path("./output/entity_id2name.json"))
save_json(filled_descriptions, Path("./output/entity_id2description.json"))
```

## Project Structure

```
text_kgc_data/
├── datasets/
│   ├── wn18rr.py        # WN18RR-specific functions
│   └── wikidata5m.py    # Wikidata5M-specific functions
├── processors.py        # General processing functions
├── truncation.py        # Text truncation utilities (new)
├── io.py               # File I/O utilities
├── cli.py              # Command-line interface
└── __init__.py         # Public API
```

## Function Naming Convention

Functions are named after **exactly what they create**:
- `create_entity_id2name_wn18rr()` → creates entity_id2name mapping
- `create_relation_id2name_wikidata5m()` → creates relation_id2name mapping  
- `fill_missing_entity_entries()` → fills missing entries in entity mappings
- `truncate_descriptions()` → truncates descriptions with dataset-aware limits
- `truncate_text_by_words()` → truncates single text by word count

## New Truncation Architecture

The toolkit now separates truncation logic into a dedicated module:
- **`truncation.py`**: Reusable truncation functions with dataset-aware limits
- **`processors.py`**: General preprocessing utilities (backward compatible)
- **Configurable**: Easy to add new datasets with custom truncation limits

## Available Commands

### WN18RR Dataset
- `text-kgc wn18rr download` - Download WN18RR data
- `text-kgc wn18rr create-entity-mappings` - Create entity ID↔name/description mappings
- `text-kgc wn18rr create-relation-mappings` - Create relation ID↔name mappings
- `text-kgc wn18rr process-pipeline` - Run complete processing pipeline

### Wikidata5M Dataset  
- `text-kgc wikidata5m download` - Download Wikidata5M data
- `text-kgc wikidata5m create-entity-mappings` - Create entity mappings
- `text-kgc wikidata5m create-relation-mappings` - Create relation mappings

### Processing
- `text-kgc fill-missing-entries` - Fill missing entries in mappings
- `text-kgc truncate-descriptions` - Truncate descriptions to token limits

## Key Design Principles

1. **Pure Functions**: Each function has clear inputs/outputs, no side effects
2. **Composable**: Functions can be chained together for complex workflows  
3. **Self-Documenting**: Function names describe exactly what they do
4. **Type Safe**: Beartype ensures type correctness at runtime
5. **Unix Philosophy**: Do one thing well, compose multiple tools

## Migration from v0.1.0

The old CLI commands map to new ones as follows:

```bash
# Old → New
tkg download-text-kgc-dataset → text-kgc wn18rr download (or wikidata5m)
tkg standardize-wn18rr-entity-files-cli → text-kgc wn18rr create-entity-mappings
tkg standardize-wn18rr-relation-file-cli → text-kgc wn18rr create-relation-mappings
tkg fill-missing-entries-cli → text-kgc fill-missing-entries
tkg truncate-description-cli → text-kgc truncate-descriptions
```

## Contributing

This project follows functional programming principles. When adding new features:

1. Create pure functions with clear inputs/outputs
2. Name functions after what they create/do
3. Add Beartype decorators for type safety
4. Include comprehensive docstrings
5. Add both CLI commands and programmatic access

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
