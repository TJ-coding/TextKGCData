# Wikidata5M Processing Guide

## Command Reference

| Command | Purpose |
|---------|---------|
| `text-kgc wikidata5m download-transductive` | Download transductive evaluation data |
| `text-kgc wikidata5m download-inductive` | Download inductive evaluation data |
| `text-kgc wikidata5m process-transductive` | Process transductive variant |
| `text-kgc wikidata5m process-inductive` | Process inductive variant |
| `text-kgc wikidata5m create-entity-text` | Create entity name/description mappings |
| `text-kgc wikidata5m create-relation-text` | Create relation name mappings |
| `text-kgc wikidata5m process-pipeline` | Complete pipeline with options |
| `text-kgc wikidata5m fill-missing-entries` | Fill missing entity entries |
| `text-kgc wikidata5m truncate-descriptions` | Truncate descriptions to word limit |

---

## Quick Start

**Single Variants:**

*Transductive Setting:*
```shell {.copy}
text-kgc wikidata5m download-transductive data/raw/wikidata5m-transductive
text-kgc wikidata5m process-transductive data/raw/wikidata5m-transductive data/standardised/wikidata5m-transductive
```

*Inductive Setting:*
```shell {.copy}
text-kgc wikidata5m download-inductive data/raw/wikidata5m-inductive
text-kgc wikidata5m process-inductive data/raw/wikidata5m-inductive data/standardised/wikidata5m-inductive
```

**All Datasets (Recommended):**
```shell {.copy}
text-kgc download-and-process-all
```

---

## Step-by-Step Processing

### Transductive Evaluation

**1. Download Transductive Dataset**
```shell {.copy}
text-kgc wikidata5m download-transductive data/raw/wikidata5m-transductive
```

**2. Process Transductive Variant**
```shell {.copy}
text-kgc wikidata5m process-transductive \
  data/raw/wikidata5m-transductive \
  data/standardised/wikidata5m-transductive
```

**3. Pipeline (Alternative)**
```shell {.copy}
text-kgc wikidata5m process-pipeline \
  data/raw/wikidata5m-transductive \
  data/standardised/wikidata5m-transductive \
  --variant transductive \
  --fill-missing \
  --truncate-descriptions \
  --max-words 50
```

### Inductive Evaluation

**1. Download Inductive Dataset**
```shell {.copy}
text-kgc wikidata5m download-inductive data/raw/wikidata5m-inductive
```

**2. Process Inductive Variant**
```shell {.copy}
text-kgc wikidata5m process-inductive \
  data/raw/wikidata5m-inductive \
  data/standardised/wikidata5m-inductive
```

**3. Pipeline (Alternative)**
```shell {.copy}
text-kgc wikidata5m process-pipeline \
  data/raw/wikidata5m-inductive \
  data/standardised/wikidata5m-inductive \
  --variant inductive \
  --fill-missing \
  --truncate-descriptions \
  --max-words 50
```

---

## Python Usage

**Transductive:**
```python {.copy}
from text_kgc_data.tkg_io import load_tkg_from_files

textual_wikidata5m_trans = load_tkg_from_files(
    "data/standardised/wikidata5m-transductive/entity_id2name.json",
    "data/standardised/wikidata5m-transductive/entity_id2description.json", 
    "data/standardised/wikidata5m-transductive/relation_id2name.json"
)
```

**Inductive:**
```python {.copy}
from text_kgc_data.tkg_io import load_tkg_from_files

textual_wikidata5m_ind = load_tkg_from_files(
    "data/standardised/wikidata5m-inductive/entity_id2name.json",
    "data/standardised/wikidata5m-inductive/entity_id2description.json", 
    "data/standardised/wikidata5m-inductive/relation_id2name.json"
)
```

---

## Preprocessing Details for Academic Papers

### Wikidata5M Dataset Specification
- **Source**: Wikidata Knowledge Graph (subset)
- **Entities**: ~5 million entities total
- **Relations**: 822 semantic relations
- **Evaluation Settings**: 
  - **Transductive**: 4,594,485 train / 23,298 validation / 23,357 test triplets
  - **Inductive**: Disjoint entity sets between train and test

### Text Processing Methodology

**Entity Name Processing:**
- Uses Wikidata entity labels as primary names
- Truncates entity names to 10 words maximum
- Handles multilingual labels (English preference)
- Example: `Q42` → `Douglas Adams`

**Entity Description Processing:**
- Sources descriptions from Wikidata entity descriptions
- Truncates to 50 words maximum using word-based splitting
- Maintains original description quality from Wikidata

**Relation Name Processing:**
- Converts Wikidata property identifiers to human-readable names
- Truncates relation names to 30 words maximum
- Example: `P31` → `instance of`

**Text Truncation:**
- Method: Word-based truncation (not subword tokenization)
- Implementation: `text.split()[:max_words]` followed by `' '.join()`
- Entity descriptions: 50 words maximum
- Relation descriptions: 30 words maximum
- Entity names: 10 words maximum (Wikidata5M specific)
- Rationale: Ensures consistent text lengths across tokenizers

**Missing Data Handling:**
- Strategy: Empty string (`''`) for missing descriptions
- No artificial placeholder tokens introduced
- Maintains data structure consistency

**Evaluation Settings:**
- **Transductive**: All entities in train/validation/test are from the same set
- **Inductive**: Test entities are disjoint from training entities
- Both settings use identical preprocessing methodology

**Text Sources:**
- Entity descriptions: Wikidata entity descriptions
- Entity names: Wikidata entity labels
- Relation names: Wikidata property labels

**Technical Specifications:**
- Character encoding: UTF-8
- Tokenizer compatibility: BERT-base-uncased (default)
- Output format: Standardized JSON mappings + plain text entity lists
- SimKGC compatibility: Full preprocessing pipeline alignment

**Citation Notes:**
This preprocessing follows SimKGC methodology (Wang et al., 2022). Word-based truncation ensures reproducibility across different tokenization schemes. For academic use, specify: "Wikidata5M entity descriptions truncated to 50 words, relation descriptions to 30 words, entity names to 10 words using word-based splitting."

---

## Paper-Ready Summary

**Copy-paste for Methods section:**

*Wikidata5M Dataset Preprocessing:* We process the Wikidata5M dataset using SimKGC-compatible preprocessing following Wang et al. (2022). The dataset supports both transductive and inductive evaluation settings with 4,594,485/23,298/23,357 train/validation/test triplets for transductive evaluation. Entity names and descriptions are sourced from Wikidata labels and descriptions respectively. Entity descriptions are truncated to 50 words, relation names to 30 words, and entity names to 10 words using word-based splitting. The inductive setting uses disjoint entity sets between training and test data to evaluate generalization to unseen entities. Missing descriptions are represented as empty strings to maintain consistent data structure.

---

## 4. Fill Missing Entity Names/Descriptions (Optional)

If you want to ensure that every entity has both a name and a description, fill missing entries with a placeholder:

```shell {.copy}
tkg fill-missing-entries-cli \
  --entity-id2name-source-path wikidata5m_tkg/entity_id2name.json \
  --entity-id2description-source-path wikidata5m_tkg/entity_id2description.json \
  --entity-id2name-save-path wikidata5m_tkg/filled_entity_id2name.json \
  --entity-id2description-save-path wikidata5m_tkg/filled_entity_id2description.json \
  --place-holder-character "-"
```

---

## 5. Truncate Descriptions (Optional, for model compatibility)

To ensure descriptions fit within a model's token limit (e.g., 50 tokens for SimKGC), run:

```shell {.copy}
tkg truncate-description-cli \
  gpt2 \
  --entity-id2description-source-path wikidata5m_tkg/filled_entity_id2description.json \
  --entity-id2description-save-path wikidata5m_tkg/truncated_entity_id2description.json \
  --truncate-tokens 50
```

---

## 6. Load the Processed Data in Python

You can now load the processed Wikidata5M files using the `load_tkg_from_files` utility:

```python {.copy}
from deer_dataset_manager.tkg_io import load_tkg_from_files

entity_id2name_source_path = "wikidata5m_tkg/filled_entity_id2name.json"  # Dict[str, str]
entity_id2description_source_path = "wikidata5m_tkg/truncated_entity_id2description.json" # Dict[str, str]
relation_id2name_source_path = "wikidata5m_tkg/relation_id2name.json" # Dict[str, str]

textual_wikidata5m_kg = load_tkg_from_files(
    entity_id2name_source_path,
    entity_id2description_source_path,
    relation_id2name_source_path,
)
```

---

## Notes
- It picks the first name out of list of names provided in the original Wikidata5M files for the entity names as well as relation names.
- All CLI commands support custom input/output paths for flexible workflows.
- You can skip steps 4 and 5 if your data is already complete and within token limits.
- For more details, see the main documentation or run `tkg --help`.
