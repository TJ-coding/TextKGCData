# TextKGCData: Textual Knowledge Graph Data Toolkit

This package provides tools for downloading, processing, and standardizing knowledge graph data with textual descriptions. It includes SimKGC-compatible preprocessing for WN18RR, FB15k-237, and Wikidata5M datasets.

---

## Getting Started
### :simple-github: Add to Your Git Project

```shell {.copy}
git submodule add https://github.com/TJ-coding/TextKGCData.git packages/text-kgc-data
```

### :simple-python: Installation

```shell {.copy}
pip install git+https://github.com/TJ-coding/TextKGCData.git@branch#subdirectory=text_kgc_data_proj
```

## :octicons-command-palette-16: Command Line Usage

### Download

All operations are available via the CLI:

```shell {.copy}
text-kgc [DATASET] [COMMAND] [OPTIONS]
```

### Batch Operations (Recommended)

**Download and Process All Datasets:**
```shell {.copy}
# Complete pipeline - downloads and processes all datasets
text-kgc download-and-process-all

# Or run separately:
text-kgc download-all      # Downloads all datasets
text-kgc process-all       # Processes all datasets
```

### Supported Datasets and Commands

**WN18RR Dataset:**
```shell {.copy}
# Download WN18RR dataset
text-kgc wn18rr download data/raw/wn18rr

# Process with SimKGC compatibility
text-kgc wn18rr process data/raw/wn18rr data/standardised/wn18rr
```

**FB15k-237 Dataset:**
```shell {.copy}
# Download FB15k-237 dataset
text-kgc fb15k237 download data/raw/fb15k237

# Process with SimKGC compatibility
text-kgc fb15k237 process data/raw/fb15k237 data/standardised/fb15k237
```

**Wikidata5M Dataset:**
```shell {.copy}
# Download transductive variant
text-kgc wikidata5m download-transductive data/raw/wikidata5m-transductive

# Download inductive variant  
text-kgc wikidata5m download-inductive data/raw/wikidata5m-inductive

# Process transductive variant
text-kgc wikidata5m process-transductive data/raw/wikidata5m-transductive data/standardised/wikidata5m-transductive

# Process inductive variant
text-kgc wikidata5m process-inductive data/raw/wikidata5m-inductive data/standardised/wikidata5m-inductive
```

### Python API

Load processed knowledge graph files:

```python
from text_kgc_data.io import load_standardized_kg

# Load all standardized data at once
kg_data = load_standardized_kg("data/standardised/wn18rr")

# Access the loaded data
entity_id2name = kg_data['entities']      # Entity ID -> name mappings
entity_id2description = kg_data['descriptions']  # Entity ID -> description mappings  
relation_id2name = kg_data['relations']   # Relation ID -> name mappings
```

Or load individual files:

```python
from text_kgc_data.io import load_json

# Load individual files manually
entity_id2name = load_json("data/standardised/<dataset>/entity_id2name.json")
entity_id2description = load_json("data/standardised/<dataset>/entity_id2description.json")
relation_id2name = load_json("data/standardised/<dataset>/relation_id2name.json")
```

Use the truncation utilities directly:

```python
from text_kgc_data.truncation import truncate_descriptions, get_truncation_limit

# Dataset-aware truncation
entity_descs = truncate_descriptions(
    entity_descriptions,
    dataset='wn18rr',
    content_type='entity'
)

# Check truncation limits
limit = get_truncation_limit('fb15k237', 'relation')  # Returns 10
```

### Key Features

- **SimKGC Compatible**: Identical preprocessing to SimKGC paper implementation
- **Dataset-Aware Truncation**: Automatic word limits per dataset (WN18RR: 50/30, FB15k-237: 50/10, Wikidata5M: 50/30)
- **Word-Based Processing**: Uses word splitting instead of tokenization for consistency
- **Multiple Variants**: Supports both transductive and inductive Wikidata5M evaluation settings

## 📖 Dataset-Specific Guides

For detailed processing instructions and academic paper preparation:

- **[WN18RR Processing Guide](wn18rr_example.md)** - WordNet knowledge graph with 40k entities
- **[FB15k-237 Processing Guide](fb15k237_example.md)** - Freebase subset with 14k entities  
- **[Wikidata5M Processing Guide](wikidata5m_example.md)** - Large-scale Wikidata with 5M entities

Each guide includes command references, step-by-step tutorials, and copy-pasteable methods sections for academic papers.

## 🔧 For Developers

- **[Adding New Datasets](adding_datasets.md)** - Complete guide for extending the toolkit with new knowledge graph datasets