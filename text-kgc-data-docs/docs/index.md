# TextKGCData: Textual Knowledge Graph Data Toolkit

This package provides tools for downloading, processing, standardizing, and loading knowledge graph data with textual descriptions. It includes a command-line interface (CLI) for all major data preparation and preprocessing steps.

---

## Add to Your Git Project
``` shell {.copy}
git submodule add https://github.com/TJ-coding/TextKGCData.git packages/text-kgc-data
```

## Installation
``` shell {.copy}
pip install git+https://github.com/TJ-coding/TextKGCData.git@branch#subdirectory=text_kgc_data_proj
```


## CLI Commands

All commands are available via the CLI defined in `text_kgc_data/cli.py`. Example usage:

```shell {.copy}
python -m text_kgc_data.cli [COMMAND] [OPTIONS]
```

### Download Data

- **download_text_kgc_dataset**
  
  Download the text-based KGC dataset from the SimKGC repository.
  
  ```shell {.copy}
  python -m text_kgc_data.cli download-text-kgc-dataset --data-dir-name <output_dir>
  ```

### Standardize WN18RR Data

- **standardize_wn18rr_entity_files_cli**
  
  Standardize WN18RR entity files (IDs, names, descriptions).
  
  ```shell {.copy}
  python -m text_kgc_data.cli standardize-wn18rr-entity-files-cli \
    --definitions-source-path WN18RR/wordnet-mlj12-definitions.txt \
    --entity-id-save-path wn18rr_tkg/entity_ids.txt \
    --entity-id2name-save-path wn18rr_tkg/entity_id2_name.txt \
    --entity-id2description-save-path wn18rr_tkg/entity_id2_description.txt
  ```

- **standardize_wn18rr_relation_file_cli**
  
  Standardize WN18RR relation file (relation IDs to descriptions).
  
  ```shell {.copy}
  python -m text_kgc_data.cli standardize-wn18rr-relation-file-cli \
    --relations-source-path WN18RR/relations.dict \
    --relation-id2name-save-path wn18rr_tkg/wn18rr-relations2description.json
  ```

### Standardize Wikidata5M Data

- **standardize_wikidata5m_entity_files_cli**
  
  Standardize Wikidata5M entity files (IDs, names, descriptions).
  
  ```shell {.copy}
  python -m text_kgc_data.cli standardize-wikidata5m-entity-files-cli \
    --entity-names-source-path wikidata5m/wikidata5m_entity.txt \
    --entity-descriptions-source-path wikidata5m/wikidata5m_text.txt \
    --entity-id-save-path wikidata5m_tkg/entity_ids.txt \
    --entity-id2name-save-path wikidata5m_tkg/entity_id2_name.json \
    --entity-id2description-save-path wikidata5m_tkg/entity_id2_description.json
  ```

- **standardize_wikidata5m_relation_file_cli**
  
  Standardize Wikidata5M relation file (relation IDs to names).
  
  ```shell {.copy}
  python -m text_kgc_data.cli standardize-wikidata5m-relation-file-cli \
    --relations-source-path wikidata5m/wikidata5m_relation.txt \
    --relation-id2name-save-path wikidata5m_tkg/relation_id2name.json
  ```

### Preprocessing Utilities

- **fill_missing_entries_cli**
  
  Fill missing entries in entity name/description JSON files with a placeholder.
  
  ```shell {.copy}
  python -m text_kgc_data.cli fill-missing-entries-cli \
    --entity-id2name-path <input_name_json> \
    --entity-id2description-path <input_desc_json> \
    --output-entity-id2name-path <output_name_json> \
    --output-entity-id2description-path <output_desc_json> \
    --place-holder-character "-"
  ```

- **truncate_description_cli**
  
  Truncate entity descriptions to a maximum number of tokens using a HuggingFace tokenizer.
  
  ```shell {.copy}
  python -m text_kgc_data.cli truncate-description-cli \
    --entity-id2description-path <input_desc_json> \
    --output-entity-id2description-path <output_desc_json> \
    --tokenizer-name <hf_tokenizer_name> \
    --truncate-tokens 50 \
    --batch-size 50000
  ```

---

## Project Layout

``` tree
text_kgc_data/
    cli.py              # Command line interface for all data operations
    download_data.py    # Downloading data from SimKGC Repo
    helpers.py          # Helper functions for TSV/JSON handling
    preprocessors.py    # Data cleaning: fill missing, truncate descriptions
    standardise_tkg_files/            
       standardise_wn18rr.py      # Standardize WN18RR dataset
       standardise_wikidata5m.py  # Standardize Wikidata5M dataset
text-kgc-data-docs/
    mkdocs.yml    # MkDocs configuration
    docs/
        index.md  # Documentation homepage
        ...       # Other markdown pages, images, files
```

---

## Loading Textual KG Files in Python

You can load processed textual knowledge graph files using the `SimKGCDataLoader`:

```python
from text_kgc_data.tkg_io import load_tkg_from_files

entity_id2name_source_path = "path/to/entity_id2name.json"  # Dict[str, str]
entity_id2description_source_path = "path/to/entity_id2description.json" # Dict[str, str]
relation_id2name_source_path = "path/to/relation_id2name.json" # Dict[str, str]

textual_kg = load_tkg_from_files(
    entity_id2name_source_path,
    entity_id2description_source_path,
    relation_id2name_source_path,
)
```

## Saving KG to Files

You can save a `TextualKG` object to disk using the `save_tkg_to_files` function. This will export the entity and relation mappings to JSON files for later use.

```python
from text_kgc_data.tkg_io import save_tkg_to_files
from text_kgc_data.tkg import TextualKG

# Assume `textual_kg` is an instance of TextualKG
save_tkg_to_files(
  textual_kg,
  "path/to/entity_id2name.json",
  "path/to/entity_id2description.json",
  "path/to/relation_id2name.json",
)
```

- Make sure the output paths are writable.
- The saved files can be loaded later using `load_tkg_from_files`.

## Notes
- All CLI commands support custom input/output paths for flexible workflows.
- Preprocessing utilities help ensure data consistency and compatibility with downstream models.
- See the code in `cli.py` for the latest available commands and options.