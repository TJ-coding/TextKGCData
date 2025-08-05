"""Data processing functions for text KGC datasets."""

from typing import Dict, List, Tuple
from beartype import beartype
from tqdm import tqdm


@beartype    
def fill_missing_entity_entries(
    entity_id2name: Dict[str, str], 
    entity_id2description: Dict[str, str], 
    placeholder_character: str = '-'
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Fill missing entries so both entity mappings have the same keys.
    
    Some entities may have names but no descriptions, or descriptions but no names.
    This function ensures both dictionaries contain the same entity IDs by filling
    missing entries with a placeholder character.
    
    Args:
        entity_id2name: Entity ID to name mapping
        entity_id2description: Entity ID to description mapping
        placeholder_character: Character to use for missing entries
        
    Returns:
        Tuple of (updated_entity_id2name, updated_entity_id2description)
    """
    entity_ids_with_name = set(entity_id2name.keys())
    entity_ids_with_desc = set(entity_id2description.keys())

    entity_ids_missing_name = entity_ids_with_desc - entity_ids_with_name
    entity_ids_missing_desc = entity_ids_with_name - entity_ids_with_desc
    
    # Create copies to avoid modifying original dictionaries
    updated_entity_id2name = entity_id2name.copy()
    updated_entity_id2description = entity_id2description.copy()
    
    # Fill missing names
    for entity_id in entity_ids_missing_name:
        updated_entity_id2name[entity_id] = placeholder_character
        
    # Fill missing descriptions
    for entity_id in entity_ids_missing_desc:
        updated_entity_id2description[entity_id] = placeholder_character
    
    return updated_entity_id2name, updated_entity_id2description


@beartype
def truncate_entity_descriptions(
    entity_id2description: Dict[str, str], 
    tokenizer_name: str,
    max_tokens: int = 50, 
    batch_size: int = 50000
) -> Dict[str, str]:
    """Truncate entity descriptions to a maximum number of tokens.
    
    Uses a HuggingFace tokenizer to truncate descriptions to the specified
    token limit. This is useful for ensuring compatibility with models that
    have input length constraints.
    
    Args:
        entity_id2description: Entity ID to description mapping
        tokenizer_name: Name of the HuggingFace tokenizer to use
        max_tokens: Maximum number of tokens per description
        batch_size: Number of descriptions to process in each batch
        
    Returns:
        Dictionary with truncated descriptions
    """
    try:
        from transformers import AutoTokenizer
    except ImportError:
        raise ImportError("transformers library is required for description truncation. Install with: pip install transformers")
    
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    
    entity_ids = list(entity_id2description.keys())
    descriptions = list(entity_id2description.values())
    
    # Process in batches to handle large datasets efficiently
    batched_entity_ids = [entity_ids[i:i + batch_size] for i in range(0, len(entity_ids), batch_size)]
    batched_descriptions = [descriptions[i:i + batch_size] for i in range(0, len(descriptions), batch_size)]
    
    truncated_entity_id2description = {}
    
    # Process each batch
    for batch_entity_ids, batch_descriptions in tqdm(
        zip(batched_entity_ids, batched_descriptions), 
        desc="Truncating descriptions", 
        total=len(batched_descriptions)
    ):
        # Tokenize and truncate
        tokens = tokenizer.batch_encode_plus(
            batch_descriptions, 
            add_special_tokens=False, 
            return_attention_mask=False, 
            return_tensors=None,
            truncation=True,
            max_length=max_tokens
        )['input_ids']
        
        # Convert back to text
        decoded_descriptions = tokenizer.batch_decode(tokens, skip_special_tokens=True)
        
        # Update the result dictionary
        for entity_id, truncated_desc in zip(batch_entity_ids, decoded_descriptions):
            truncated_entity_id2description[entity_id] = truncated_desc
    
    return truncated_entity_id2description


@beartype
def validate_entity_mappings(
    entity_id2name: Dict[str, str], 
    entity_id2description: Dict[str, str]
) -> Tuple[bool, List[str]]:
    """Validate that entity mappings are consistent.
    
    Args:
        entity_id2name: Entity ID to name mapping
        entity_id2description: Entity ID to description mapping
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check for empty values
    empty_names = [eid for eid, name in entity_id2name.items() if not name.strip()]
    empty_descriptions = [eid for eid, desc in entity_id2description.items() if not desc.strip()]
    
    if empty_names:
        issues.append(f"Found {len(empty_names)} entities with empty names")
    
    if empty_descriptions:
        issues.append(f"Found {len(empty_descriptions)} entities with empty descriptions")
    
    # Check for missing entities
    name_ids = set(entity_id2name.keys())
    desc_ids = set(entity_id2description.keys())
    
    missing_names = desc_ids - name_ids
    missing_descriptions = name_ids - desc_ids
    
    if missing_names:
        issues.append(f"Found {len(missing_names)} entities with descriptions but no names")
    
    if missing_descriptions:
        issues.append(f"Found {len(missing_descriptions)} entities with names but no descriptions")
    
    is_valid = len(issues) == 0
    return is_valid, issues
