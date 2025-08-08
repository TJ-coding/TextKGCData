"""Text processing utilities for knowledge graph data."""

from typing import Dict, Optional, Tuple
from .truncation import truncate_descriptions


def fill_missing_entity_entries(
    entity_id2name: Dict[str, str],
    entity_id2description: Dict[str, str]
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Fill missing entries between entity name and description mappings.
    
    Args:
        entity_id2name: Entity ID to name mapping
        entity_id2description: Entity ID to description mapping
        
    Returns:
        Tuple of (filled_names, filled_descriptions) with missing entries filled
    """
    all_entity_ids = set(entity_id2name.keys()) | set(entity_id2description.keys())
    
    filled_names = {}
    filled_descriptions = {}
    
    for entity_id in all_entity_ids:
        filled_names[entity_id] = entity_id2name.get(entity_id, '')
        filled_descriptions[entity_id] = entity_id2description.get(entity_id, '')
    
    return filled_names, filled_descriptions


def validate_entity_mappings(
    entity_id2name: Dict[str, str],
    entity_id2description: Dict[str, str]
) -> bool:
    """Validate entity mappings for consistency.
    
    Args:
        entity_id2name: Entity ID to name mapping
        entity_id2description: Entity ID to description mapping
        
    Returns:
        True if mappings are valid
    """
    # Simple validation - check for empty keys
    for entity_id in entity_id2name:
        if not entity_id.strip():
            return False
    
    for entity_id in entity_id2description:
        if not entity_id.strip():
            return False
    
    return True


def truncate_entity_descriptions(
    descriptions: Dict[str, str], 
    max_words: int = 50,
    dataset: Optional[str] = None,
    content_type: Optional[str] = None
) -> Dict[str, str]:
    """Truncate entity/relation descriptions using word-based truncation.
    
    This function implements SimKGC-compatible word-based truncation, where
    text is split by whitespace and only the first max_words words are kept.
    
    This is a backward-compatible wrapper around the new truncation module.
    
    Args:
        descriptions: Dictionary mapping IDs to text descriptions
        max_words: Maximum number of words to keep (default: 50)
        dataset: Dataset name for dataset-aware truncation ('wn18rr', 'fb15k237', 'wikidata5m')
        content_type: Type of content ('entity' or 'relation') for dataset-aware truncation
        
    Returns:
        Dictionary with truncated descriptions
    """
    return truncate_descriptions(descriptions, max_words, dataset, content_type)


def clean_wn18rr_entity_name(entity_name: str) -> str:
    """Clean WN18RR entity names by removing __ prefix.
    
    SimKGC removes the __ prefix from WN18RR entity names during preprocessing.
    
    Args:
        entity_name: Raw entity name from WN18RR
        
    Returns:
        Cleaned entity name with __ prefix removed
    """
    return entity_name.replace('__', '')


def preprocess_triplet_data(
    triplets_file: str,
    entity_descriptions: Dict[str, str],
    relation_descriptions: Dict[str, str],
    output_file: str,
    dataset: str = "wn18rr"
) -> None:
    """Preprocess triplet data with entity and relation descriptions.
    
    Args:
        triplets_file: Path to input triplets file
        entity_descriptions: Entity ID to description mapping
        relation_descriptions: Relation ID to description mapping  
        output_file: Path to output processed file
        dataset: Dataset name for appropriate processing
    """
    with open(triplets_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                head, relation, tail = parts[:3]
                
                # Get descriptions (use empty string if not found)
                head_desc = entity_descriptions.get(head, '')
                tail_desc = entity_descriptions.get(tail, '')
                rel_desc = relation_descriptions.get(relation, '')
                
                # Apply dataset-specific cleaning
                if dataset.lower() == 'wn18rr':
                    head_desc = clean_wn18rr_entity_name(head_desc)
                    tail_desc = clean_wn18rr_entity_name(tail_desc)
                
                # Write processed triplet with descriptions
                outfile.write(f"{head}\t{relation}\t{tail}\t{head_desc}\t{rel_desc}\t{tail_desc}\n")
