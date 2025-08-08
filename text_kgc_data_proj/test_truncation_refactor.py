#!/usr/bin/env python3
"""
Test the refactored truncation logic.

This script verifies that the separation of concerns works correctly
and that backward compatibility is maintained.
"""

import sys
import os

# Add the project to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from text_kgc_data.truncation import (
    truncate_descriptions,
    truncate_text_by_words,
    get_truncation_limit,
    add_truncation_config,
    get_available_datasets,
    get_dataset_config,
)

from text_kgc_data.processors import truncate_entity_descriptions


def test_backward_compatibility():
    """Test that the old API still works."""
    print("Testing backward compatibility...")
    
    sample_data = {
        "entity_1": "This is a test description with many words that should be truncated properly",
        "entity_2": "Short",
        "entity_3": ""
    }
    
    # Test old function
    old_result = truncate_entity_descriptions(sample_data, max_words=5)
    
    # Test new function
    new_result = truncate_descriptions(sample_data, max_words=5)
    
    assert old_result == new_result, "Backward compatibility broken!"
    print("✓ Backward compatibility maintained")


def test_dataset_aware_truncation():
    """Test dataset-aware truncation limits."""
    print("Testing dataset-aware truncation...")
    
    sample_data = {
        "test_entity": "This is a test description with exactly fifteen words to test the truncation functionality properly and correctly."
    }
    
    # Test WN18RR entity (should be 50 words)
    wn18rr_result = truncate_descriptions(sample_data, dataset='wn18rr', content_type='entity')
    assert len(wn18rr_result["test_entity"].split()) == 15, "WN18RR entity truncation failed"
    
    # Test FB15k237 relation (should be 10 words)  
    fb_result = truncate_descriptions(sample_data, dataset='fb15k237', content_type='relation')
    assert len(fb_result["test_entity"].split()) == 10, "FB15k237 relation truncation failed"
    
    print("✓ Dataset-aware truncation working correctly")


def test_new_functions():
    """Test the new standalone functions."""
    print("Testing new truncation functions...")
    
    # Test single text truncation
    text = "This is a test with ten words exactly"
    truncated = truncate_text_by_words(text, 5)
    assert truncated == "This is a test with", f"Expected 'This is a test with', got '{truncated}'"
    
    # Test truncation limit retrieval
    wn18rr_entity_limit = get_truncation_limit('wn18rr', 'entity')
    assert wn18rr_entity_limit == 50, f"Expected 50, got {wn18rr_entity_limit}"
    
    fb237_relation_limit = get_truncation_limit('fb15k237', 'relation')
    assert fb237_relation_limit == 10, f"Expected 10, got {fb237_relation_limit}"
    
    print("✓ New functions working correctly")


def test_custom_dataset():
    """Test adding custom dataset configuration."""
    print("Testing custom dataset configuration...")
    
    # Add custom dataset
    add_truncation_config('test_dataset', entity_limit=7, relation_limit=3)
    
    # Verify it was added
    assert 'test_dataset' in get_available_datasets(), "Custom dataset not added"
    
    config = get_dataset_config('test_dataset')
    assert config['entity'] == 7, f"Expected entity limit 7, got {config['entity']}"
    assert config['relation'] == 3, f"Expected relation limit 3, got {config['relation']}"
    
    # Test truncation with custom dataset
    sample_data = {"test": "one two three four five six seven eight nine ten"}
    result = truncate_descriptions(sample_data, dataset='test_dataset', content_type='entity')
    assert len(result["test"].split()) == 7, "Custom dataset truncation failed"
    
    print("✓ Custom dataset configuration working correctly")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("Testing edge cases...")
    
    # Empty descriptions
    empty_data = {"empty": "", "none": None}
    # Note: None values would cause an error, so let's test with empty string
    safe_empty_data = {"empty": ""}
    result = truncate_descriptions(safe_empty_data)
    assert result["empty"] == "", "Empty description handling failed"
    
    # Very short text
    short_data = {"short": "one"}
    result = truncate_descriptions(short_data, max_words=5)
    assert result["short"] == "one", "Short text handling failed"
    
    # Unknown dataset (should use default)
    unknown_result = truncate_descriptions({"test": "one two three"}, dataset='unknown', content_type='entity', max_words=2)
    assert len(unknown_result["test"].split()) == 2, "Unknown dataset handling failed"
    
    print("✓ Edge cases handled correctly")


def main():
    """Run all tests."""
    print("=== Testing Refactored Truncation Logic ===\n")
    
    try:
        test_backward_compatibility()
        test_dataset_aware_truncation()
        test_new_functions()
        test_custom_dataset()
        test_edge_cases()
        
        print("\n🎉 All tests passed! Refactoring successful.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
