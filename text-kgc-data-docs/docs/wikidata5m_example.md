# Tutorial: Processing Wikidata5M Data with TextKGCData CLI

This tutorial guides you through the complete workflow for processing the Wikidata5M dataset using the TextKGCData CLI, from downloading the raw data to loading the processed files for use in your code.

---

## 1. Download the Wikidata5M Dataset

First, download the text-based KGC dataset (including Wikidata5M) from the SimKGC repository:

```shell {.copy}
tkg download-text-kgc-dataset --data-dir-name wikidata5m
```

This will create a directory (default: `wikidata5m/`) with the raw data files.

---

## 2. Standardize Entity Files

Convert the raw Wikidata5M entity files into standardized files for entity IDs, names, and descriptions:

```shell {.copy}
tkg standardize-wikidata5m-entity-files-cli \
  --entity-names-source-path wikidata5m/wikidata5m_entity.txt \
  --entity-descriptions-source-path wikidata5m/wikidata5m_text.txt \
  --entity-id-save-path wikidata5m_tkg/entity_ids.txt \
  --entity-id2name-save-path wikidata5m_tkg/entity_id2_name.json \
  --entity-id2description-save-path wikidata5m_tkg/entity_id2_description.json
```

This will generate:
- `wikidata5m_tkg/entity_ids.txt`
- `wikidata5m_tkg/entity_id2_name.json`
- `wikidata5m_tkg/entity_id2_description.json`

---

## 3. Standardize Relation File

Convert the raw Wikidata5M relations file into a standardized JSON mapping:

```shell {.copy}
tkg standardize-wikidata5m-relation-file-cli \
  --relations-source-path wikidata5m/wikidata5m_relation.txt \
  --relation-id2name-save-path wikidata5m_tkg/relation_id2name.json
```

This will generate:
- `wikidata5m_tkg/relation_id2name.json`

---

## 4. Fill Missing Entity Names/Descriptions (Optional)

If you want to ensure that every entity has both a name and a description, fill missing entries with a placeholder:

```shell {.copy}
tkg fill-missing-entries-cli \
  --entity-id2name-source-path wikidata5m_tkg/entity_id2_name.json \
  --entity-id2description-source-path wikidata5m_tkg/entity_id2_description.json \
  --entity-id2name-save-path wikidata5m_tkg/filled_entity_id2_name.json \
  --entity-id2description-save-path wikidata5m_tkg/filled_entity_id2_description.json \
  --place-holder-character "-"
```

---

## 5. Truncate Descriptions (Optional, for model compatibility)

To ensure descriptions fit within a model's token limit (e.g., 50 tokens for SimKGC), run:

```shell {.copy}
tkg truncate-description-cli \
  --tokenizer-name bert-base-uncased \
  --entity-id2description-path wikidata5m_tkg/filled_entity_id2_description.json \
  --output-entity-id2description-path wikidata5m_tkg/truncated_entity_id2_description.json \
  --truncate-tokens 50
```

---

## 6. Load the Processed Data in Python

You can now load the processed Wikidata5M files using the `load_tkg_from_files` utility:

```python {.copy}
from deer_dataset_manager.tkg_io import load_tkg_from_files

entity_id2name_source_path = "wikidata5m_tkg/filled_entity_id2_name.json"  # Dict[str, str]
entity_id2description_source_path = "wikidata5m_tkg/truncated_entity_id2_description.json" # Dict[str, str]
relation_id2name_source_path = "wikidata5m_tkg/relation_id2name.json" # Dict[str, str]

textual_wikidata5m_kg = load_tkg_from_files(
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
