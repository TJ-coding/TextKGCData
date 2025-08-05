#!/usr/bin/env python3
"""
Simple test to verify the refactored structure works correctly.
This tests the import structure and basic functionality.
"""

import sys
from pathlib import Path

# Add the package to the path for testing
package_path = Path(__file__).parent / "text_kgc_data_proj"
sys.path.insert(0, str(package_path))

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        # Test main package import
        import text_kgc_data
        print("✅ Main package import successful")
        
        # Test dataset imports
        from text_kgc_data.datasets import wn18rr, wikidata5m
        print("✅ Dataset module imports successful")
        
        # Test specific function imports
        from text_kgc_data.datasets.wn18rr import create_entity_id2name_wn18rr
        from text_kgc_data.datasets.wikidata5m import create_entity_id2name_wikidata5m
        print("✅ Specific function imports successful")
        
        # Test processor imports
        from text_kgc_data.processors import fill_missing_entity_entries
        print("✅ Processor imports successful")
        
        # Test I/O imports
        from text_kgc_data.io import save_json, load_json
        print("✅ I/O imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_function_signatures():
    """Test that functions have the expected signatures."""
    print("\nTesting function signatures...")
    
    try:
        from text_kgc_data.datasets.wn18rr import create_entity_id2name_wn18rr
        from text_kgc_data.processors import fill_missing_entity_entries
        
        # Check function docstrings exist
        assert create_entity_id2name_wn18rr.__doc__ is not None
        assert "entity_id2name" in create_entity_id2name_wn18rr.__doc__
        print("✅ Function docstrings present")
        
        assert fill_missing_entity_entries.__doc__ is not None
        assert "missing entries" in fill_missing_entity_entries.__doc__.lower()
        print("✅ Processor function documentation present")
        
        return True
        
    except Exception as e:
        print(f"❌ Function signature test error: {e}")
        return False

def test_api_exports():
    """Test that the main API exports work."""
    print("\nTesting API exports...")
    
    try:
        import text_kgc_data
        
        # Check some key functions are exported
        expected_exports = [
            'create_entity_id2name_wn18rr',
            'create_entity_id2description_wn18rr',
            'fill_missing_entity_entries',
            'save_json',
            'load_json'
        ]
        
        for export in expected_exports:
            assert hasattr(text_kgc_data, export), f"Missing export: {export}"
        
        print("✅ API exports present")
        return True
        
    except Exception as e:
        print(f"❌ API export test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing TextKGCData refactored structure...\n")
    
    tests = [
        test_imports,
        test_function_signatures,
        test_api_exports,
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Refactoring successful.")
        return 0
    else:
        print("❌ Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
