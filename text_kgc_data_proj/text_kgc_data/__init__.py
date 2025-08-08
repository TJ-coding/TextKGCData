"""Text Knowledge Graph Completion Data Toolkit.

A simple, functional toolkit for downloading, processing, and working with 
knowledge graph datasets for text-based knowledge graph completion.

Usage:
    # CLI usage
    text-kgc wn18rr download ./data
    text-kgc wn18rr create-entity-mappings ./data/WN18RR/wordnet-mlj12-definitions.txt ./output
    
    # Programmatic usage
    from text_kgc_data.datasets.wn18rr import create_entity_id2name_wn18rr
    entity_mapping = create_entity_id2name_wn18rr(Path("definitions.txt"))
"""

# Import main functions for programmatic usage
from text_kgc_data.datasets.wn18rr import (
    download_wn18rr,
    create_entity_id2name_wn18rr,
    create_entity_id2description_wn18rr,
    create_relation_id2name_wn18rr,
)

from text_kgc_data.datasets.wikidata5m import (
    download_wikidata5m,
    create_entity_id2name_wikidata5m,
    create_entity_id2description_wikidata5m,
    create_relation_id2name_wikidata5m,
)

from text_kgc_data.processors import (
    fill_missing_entity_entries,
    truncate_entity_descriptions,
    validate_entity_mappings,
)

from text_kgc_data.truncation import (
    truncate_descriptions,
    truncate_text_by_words,
    get_truncation_limit,
    add_truncation_config,
    get_available_datasets,
    get_dataset_config,
)

from text_kgc_data.io import (
    load_json,
    save_json,
    save_entity_ids_list,
    load_standardized_kg,
)

__version__ = "0.2.0"
__all__ = [
    # WN18RR functions
    "download_wn18rr",
    "create_entity_id2name_wn18rr", 
    "create_entity_id2description_wn18rr",
    "create_relation_id2name_wn18rr",
    
    # Wikidata5M functions
    "download_wikidata5m",
    "create_entity_id2name_wikidata5m",
    "create_entity_id2description_wikidata5m", 
    "create_relation_id2name_wikidata5m",
    
    # Processing functions
    "fill_missing_entity_entries",
    "truncate_entity_descriptions",
    "validate_entity_mappings",
    
    # Truncation functions (new)
    "truncate_descriptions",
    "truncate_text_by_words", 
    "get_truncation_limit",
    "add_truncation_config",
    "get_available_datasets",
    "get_dataset_config",
    
    # I/O functions
    "load_json",
    "save_json",
    "save_entity_ids_list",
    "load_standardized_kg",
]
