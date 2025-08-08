# FB15k-237 Processing Guide

## Command Reference

| Command | Purpose |
|---------|---------|
| `text-kgc fb15k237 download` | Download raw FB15k-237 dataset |
| `text-kgc fb15k237 process` | Complete SimKGC-compatible processing |
| `text-kgc fb15k237 create-entity-text` | Create entity name/description mappings |
| `text-kgc fb15k237 create-relation-text` | Create relation name mappings |
| `text-kgc fb15k237 process-pipeline` | Complete pipeline with options |
| `text-kgc fb15k237 fill-missing-entries` | Fill missing entity entries |
| `text-kgc fb15k237 truncate-descriptions` | Truncate descriptions to word limit |

---

## Quick Start

**Single Dataset (FB15k-237 only):**
```shell {.copy}
text-kgc fb15k237 download data/raw/fb15k237
text-kgc fb15k237 process data/raw/fb15k237 data/standardised/fb15k237
```

**All Datasets (Recommended):**
```shell {.copy}
text-kgc download-and-process-all
```

---

## Step-by-Step Processing

**1. Download Dataset**
```shell {.copy}
text-kgc fb15k237 download data/raw/fb15k237
```

**2. Create Entity Text**
```shell {.copy}
text-kgc fb15k237 create-entity-text \
  data/raw/fb15k237/FB15k_mid2description.txt \
  data/standardised/fb15k237
```

**3. Create Relation Text**
```shell {.copy}
text-kgc fb15k237 create-relation-text \
  data/raw/fb15k237/relations.dict \
  data/standardised/fb15k237
```

**4. Pipeline (Alternative)**
```shell {.copy}
text-kgc fb15k237 process-pipeline \
  data/raw/fb15k237 \
  data/standardised/fb15k237 \
  --fill-missing \
  --truncate-descriptions \
  --max-words 50
```

---

## Python Usage

```python {.copy}
from text_kgc_data.tkg_io import load_tkg_from_files

textual_fb15k237_kg = load_tkg_from_files(
    "data/standardised/fb15k237/entity_id2name.json",
    "data/standardised/fb15k237/entity_id2description.json", 
    "data/standardised/fb15k237/relation_id2name.json"
)
```

---

## Preprocessing Details for Academic Papers

### FB15k-237 Dataset Specification
- **Source**: Freebase Knowledge Graph (filtered subset)
- **Entities**: 14,541 unique entities
- **Relations**: 237 semantic relations  
- **Splits**: 272,115 train / 17,535 validation / 20,466 test triplets

### Text Processing Methodology

**Entity Name Cleaning:**
- Removes namespace prefixes from Freebase entity identifiers
- Converts underscores to spaces for readability
- Example transformation: `/m/02mjmr` → entity name from mid2name mapping

**Relation Name Processing:**
- Removes namespace prefixes (e.g., `/base/`, `/people/`)
- Converts forward slashes to spaces
- Deduplicates consecutive identical tokens
- Example transformation: `/people/person/nationality` → `nationality person people`

**Text Truncation:**
- Method: Word-based truncation (not subword tokenization)
- Implementation: `text.split()[:max_words]` followed by `' '.join()`
- Entity descriptions: 50 words maximum
- Relation descriptions: 10 words maximum (FB15k-237 specific)
- Rationale: Ensures consistent text lengths across tokenizers

**Missing Data Handling:**
- Strategy: Empty string (`''`) for missing descriptions
- No artificial placeholder tokens introduced
- Maintains data structure consistency

**Text Sources:**
- Entity descriptions: `FB15k_mid2description.txt`
- Entity names: `FB15k_mid2name.txt`
- Relation names: Derived from relation identifiers with cleaning

**Technical Specifications:**
- Character encoding: UTF-8
- Tokenizer compatibility: BERT-base-uncased (default)
- Output format: Standardized JSON mappings + plain text entity lists
- SimKGC compatibility: Full preprocessing pipeline alignment

**Citation Notes:**
This preprocessing follows SimKGC methodology (Wang et al., 2022). Word-based truncation ensures reproducibility across different tokenization schemes. For academic use, specify: "FB15k-237 entity descriptions truncated to 50 words, relation descriptions to 10 words using word-based splitting."

---

## Paper-Ready Summary

**Copy-paste for Methods section:**

*FB15k-237 Dataset Preprocessing:* We process the FB15k-237 dataset using SimKGC-compatible preprocessing following Wang et al. (2022). The dataset contains 14,541 entities and 237 relations with 272,115/17,535/20,466 train/validation/test triplets. Entity names and descriptions are sourced from Freebase mid-to-name and mid-to-description mappings. Entity descriptions are truncated to 50 words and relation names to 10 words using word-based splitting. Relation names undergo namespace cleaning by removing prefixes like `/people/` and converting forward slashes to spaces. Missing descriptions are represented as empty strings to maintain consistent data structure.
