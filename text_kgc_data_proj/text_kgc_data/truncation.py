"""Text truncation utilities for knowledge graph data.

This module provides reusable truncation functions that can be used across
different datasets and content types.
"""

from typing import Dict, Optional, Union

import tqdm


# Dataset-specific truncation configuration
TRUNCATION_CONFIGS = {
    'wn18rr': {
        'entity': 50,
        'relation': 30
    },
    'fb15k237': {
        'entity': 50, 
        'relation': 10
    },
    'wikidata5m': {
        'entity': 50,
        'relation': 30
    }
}


def get_truncation_limit(
    dataset: Optional[str] = None,
    content_type: Optional[str] = None,
    default_limit: int = 50
) -> int:
    """Get the appropriate truncation limit for a dataset and content type.
    
    Args:
        dataset: Dataset name ('wn18rr', 'fb15k237', 'wikidata5m')
        content_type: Type of content ('entity' or 'relation')
        default_limit: Default limit if dataset/content_type not found
        
    Returns:
        Appropriate word limit for truncation
    """
    if not dataset or not content_type:
        return default_limit
        
    dataset_key = dataset.lower()
    content_key = content_type.lower()
    
    if dataset_key in TRUNCATION_CONFIGS:
        config = TRUNCATION_CONFIGS[dataset_key]
        if content_key in config:
            return config[content_key]
    
    return default_limit


def truncate_text_by_words(
    text: str,
    max_words: int,
    preserve_empty: bool = True
) -> str:
    """Truncate text using word-based truncation.
    
    This function implements SimKGC-compatible word-based truncation, where
    text is split by whitespace and only the first max_words words are kept.
    
    Args:
        text: Input text to truncate
        max_words: Maximum number of words to keep
        preserve_empty: If True, return empty string for empty input
        
    Returns:
        Truncated text
    """
    if not text or not text.strip():
        return '' if preserve_empty else text
    
    # Word-based truncation: split by whitespace and take first max_words words
    words = text.split()
    return ' '.join(words[:max_words])


def truncate_descriptions(
    descriptions: Dict[str, str], 
    max_words: int = 50,
    dataset: Optional[str] = None,
    content_type: Optional[str] = None
) -> Dict[str, str]:
    """Truncate a dictionary of descriptions using word-based truncation.
    
    This function implements SimKGC-compatible word-based truncation with
    optional dataset-aware limits.
    
    Args:
        descriptions: Dictionary mapping IDs to text descriptions
        max_words: Maximum number of words to keep (default: 50)
        dataset: Dataset name for dataset-aware truncation
        content_type: Type of content ('entity' or 'relation') for dataset-aware truncation
        
    Returns:
        Dictionary with truncated descriptions
    """
    # Get dataset-aware truncation limit
    effective_limit = get_truncation_limit(dataset, content_type, max_words)
    
    truncated = {}
    for item_id, description in tqdm.tqdm(descriptions.items(), desc="Truncating descriptions"):
        truncated[item_id] = truncate_text_by_words(
            description, 
            effective_limit,
            preserve_empty=True
        )
    
    return truncated


def add_truncation_config(
    dataset: str,
    entity_limit: int,
    relation_limit: int
) -> None:
    """Add or update truncation configuration for a dataset.
    
    This allows dynamic addition of new dataset configurations.
    
    Args:
        dataset: Dataset name
        entity_limit: Word limit for entity descriptions
        relation_limit: Word limit for relation descriptions
    """
    TRUNCATION_CONFIGS[dataset.lower()] = {
        'entity': entity_limit,
        'relation': relation_limit
    }


def get_available_datasets() -> list:
    """Get list of datasets with configured truncation limits.
    
    Returns:
        List of available dataset names
    """
    return list(TRUNCATION_CONFIGS.keys())


def get_dataset_config(dataset: str) -> Dict[str, int]:
    """Get truncation configuration for a specific dataset.
    
    Args:
        dataset: Dataset name
        
    Returns:
        Dictionary with entity and relation limits
        
    Raises:
        KeyError: If dataset not found in configuration
    """
    dataset_key = dataset.lower()
    if dataset_key not in TRUNCATION_CONFIGS:
        raise KeyError(f"Dataset '{dataset}' not found in truncation configuration")
    
    return TRUNCATION_CONFIGS[dataset_key].copy()
