#!/usr/bin/env python3
"""
Example demonstrating the new truncation utilities.

This script shows how to use the separated truncation logic for different
datasets and content types.
"""

from text_kgc_data.truncation import (
    truncate_descriptions,
    truncate_text_by_words,
    get_truncation_limit,
    add_truncation_config,
    get_available_datasets,
    get_dataset_config,
)


def main():
    print("=== TextKGCData Truncation Examples ===\n")
    
    # Example 1: Basic text truncation
    print("1. Basic text truncation:")
    long_text = "This is a very long description that should be truncated to a reasonable length for processing in knowledge graph models."
    truncated = truncate_text_by_words(long_text, max_words=10)
    print(f"Original: {long_text}")
    print(f"Truncated (10 words): {truncated}\n")
    
    # Example 2: Dataset-aware truncation limits
    print("2. Dataset-aware truncation limits:")
    for dataset in get_available_datasets():
        entity_limit = get_truncation_limit(dataset, 'entity')
        relation_limit = get_truncation_limit(dataset, 'relation')
        print(f"{dataset.upper()}: entity={entity_limit} words, relation={relation_limit} words")
    print()
    
    # Example 3: Truncating descriptions for different datasets
    print("3. Dataset-specific description truncation:")
    sample_descriptions = {
        "entity_1": "This is an entity with a moderately long description that needs truncation",
        "entity_2": "Short desc",
        "entity_3": "Another very long entity description that exceeds typical limits and should be truncated appropriately for the target dataset",
        "entity_4": ""  # Empty description
    }
    
    for dataset in ['wn18rr', 'fb15k237', 'wikidata5m']:
        print(f"\n{dataset.upper()} entity truncation:")
        truncated = truncate_descriptions(
            sample_descriptions, 
            dataset=dataset, 
            content_type='entity'
        )
        
        for entity_id, desc in truncated.items():
            original_len = len(sample_descriptions[entity_id].split())
            truncated_len = len(desc.split()) if desc else 0
            print(f"  {entity_id}: {original_len} → {truncated_len} words")
            if desc:
                print(f"    \"{desc}\"")
            else:
                print(f"    (empty)")
    
    # Example 4: Adding custom dataset configuration
    print("\n4. Adding custom dataset configuration:")
    add_truncation_config('custom_kg', entity_limit=25, relation_limit=15)
    print(f"Added custom_kg to available datasets: {get_available_datasets()}")
    
    custom_config = get_dataset_config('custom_kg')
    print(f"Custom KG config: {custom_config}")
    
    # Demonstrate custom truncation
    custom_truncated = truncate_descriptions(
        sample_descriptions,
        dataset='custom_kg',
        content_type='entity'
    )
    print(f"Custom KG entity truncation (limit: {custom_config['entity']}):")
    for entity_id, desc in custom_truncated.items():
        word_count = len(desc.split()) if desc else 0
        print(f"  {entity_id}: {word_count} words - \"{desc}\"")
    
    # Example 5: Manual truncation without dataset awareness
    print("\n5. Manual truncation (no dataset awareness):")
    manual_truncated = truncate_descriptions(sample_descriptions, max_words=8)
    for entity_id, desc in manual_truncated.items():
        word_count = len(desc.split()) if desc else 0
        print(f"  {entity_id}: {word_count} words - \"{desc}\"")


if __name__ == "__main__":
    main()
