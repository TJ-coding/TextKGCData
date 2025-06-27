# Tutorial: Processing WN18RR Data with TextKGCData CLI

This tutorial walks you through the complete workflow for processing the WN18RR dataset using the TextKGCData CLI, from downloading the raw data to loading the processed files for use in your code.

---

## 1. Download the WN18RR Dataset

First, download the text-based KGC dataset (including WN18RR) from the SimKGC repository:

```shell {.copy}
tkg download-text-kgc-dataset --data-dir-name WN18RR
```

This will create a directory (default: `WN18RR/`) with the raw data files.

---

## 2. Standardize Entity Files

Convert the raw WN18RR entity definitions into standardized files for entity IDs, names, and descriptions:

```shell {.copy}
tkg standardize-wn18rr-entity-files-cli \
  --definitions-source-path WN18RR/wordnet-mlj12-definitions.txt \
  --entity-id-save-path wn18rr_tkg/entity_ids.txt \
  --entity-id2name-save-path wn18rr_tkg/entity_id2name.json \
  --entity-id2description-save-path wn18rr_tkg/entity_id2description.json
```

This will generate:
- `wn18rr_tkg/entity_ids.txt`
- `wn18rr_tkg/entity_id2name.json`
- `wn18rr_tkg/entity_id2description.json`

---

## 3. Standardize Relation File

Convert the raw WN18RR relations file into a standardized JSON mapping:

```shell {.copy}
tkg standardize-wn18rr-relation-file-cli \
  --relations-source-path WN18RR/relations.dict \
  --relation-id2name-save-path wn18rr_tkg/relation_id2name.json
```

This will generate:
- `wn18rr_tkg/wn18rr-relations2description.json`

---

## 4. Fill Missing Entity Names/Descriptions (Optional)

If you want to ensure that every entity has both a name and a description, fill missing entries with a placeholder:

```shell {.copy}
tkg fill-missing-entries-cli \
  --entity-id2name-source-path wn18rr_tkg/entity_id2name.json \
  --entity-id2description-source-path wn18rr_tkg/entity_id2description.json \
  --entity-id2name-save-path wn18rr_tkg/filled_entity_id2name.json \
  --entity-id2description-save-path wn18rr_tkg/filled_entity_id2description.json \
  --place-holder-character "-"
```

---

## 5. Truncate Descriptions (Optional, for model compatibility)

To ensure descriptions fit within a model's token limit (e.g., 50 tokens for SimKGC), run:

```shell {.copy}
tkg truncate-description-cli \
  gpt2 \
  --entity-id2description-source-path wn18rr_tkg/filled_entity_id2description.json \
  --entity-id2description-save-path wn18rr_tkg/truncated_entity_id2description.json \
  --truncate-tokens 50
```

---

## 6. Load the Processed Data in Python

You can now load the processed WN18RR files using the `SimKGCDataLoader`:

```python {.copy}
from deer_dataset_manager.tkg_io import load_tkg_from_files

entity_id2name_source_path = "wn18rr_tkg/filled_entity_id2name.json"  # Dict[str, str]
entity_id2description_source_path = "wn18rr_tkg/truncated_entity_id2description.json" # Dict[str, str]
relation_id2name_source_path = "wn18rr_tkg/relation_id2name.json" # Dict[str, str]

textual_wn18rr_kg = load_tkg_from_files(
    entity_id2name_source_path,
    entity_id2description_source_path,
    relation_id2name_source_path,
)
```

---

## Notes
- All CLI commands support custom input/output paths for flexible workflows.
- You can skip steps 4 and 5 if your data is already complete and within token limits.
- For more details, see the main documentation or run `tkg --help`.
