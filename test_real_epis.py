#!/usr/bin/env python3
"""
Standalone test runner for real ePIs - Model and Logic Testing

This script tests the FhirEPI model and preprocessing logic
with actual ePI documents from the testing folder
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from preprocessor.models.fhir_epi import FhirEPI


def load_test_epis():
    """Load all test ePIs from the testing folder"""
    # Try multiple possible locations
    possible_paths = [
        Path(__file__).parent / "preprocessor" / "test" / "testing ePIs",
        Path(__file__).parent.parent / "preprocessor" / "test" / "testing ePIs",
        Path.cwd() / "preprocessor" / "test" / "testing ePIs",
    ]
    
    test_folder = None
    for p in possible_paths:
        if p.exists():
            test_folder = p
            break
    
    test_epis = {}
    
    if test_folder is None:
        print(f"ERROR: Testing ePIs folder not found")
        print(f"Tried: {', '.join(str(p) for p in possible_paths)}")
        return test_epis
    
    for json_file in sorted(test_folder.glob("*.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                test_epis[json_file.stem] = data
        except Exception as e:
            print(f"Warning: Could not load {json_file.name}: {e}")
    
    return test_epis


def test_basic_structure(test_epis):
    """Test basic structure of all ePIs"""
    print("\n" + "=" * 70)
    print("TEST 1: Basic FHIR Bundle Structure")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for name, epi_data in test_epis.items():
        try:
            assert 'resourceType' in epi_data, "Missing resourceType"
            assert epi_data['resourceType'] == 'Bundle', f"Not a Bundle: {epi_data['resourceType']}"
            assert 'type' in epi_data, "Missing type"
            assert epi_data['type'] == 'document', f"Not a document: {epi_data['type']}"
            assert 'entry' in epi_data, "Missing entry array"
            assert isinstance(epi_data['entry'], list), "entry is not a list"
            assert len(epi_data['entry']) > 0, "entry array is empty"
            
            print(f"[PASS] {name}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_model_creation(test_epis):
    """Test creating FhirEPI model from all ePIs"""
    print("\n" + "=" * 70)
    print("TEST 2: FhirEPI Model Creation")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for name, epi_data in test_epis.items():
        try:
            epi = FhirEPI.from_dict(epi_data)
            assert epi.resource_type == 'Bundle', "Model resourceType incorrect"
            assert epi.type == 'document', "Model type incorrect"
            assert epi.entry is not None, "Model entry is None"
            assert len(epi.entry) > 0, "Model entry is empty"
            
            print(f"[PASS] {name} ({len(epi.entry)} entries)")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_serialization(test_epis):
    """Test serializing models back to dict"""
    print("\n" + "=" * 70)
    print("TEST 3: Serialization to Dictionary")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for name, epi_data in test_epis.items():
        try:
            epi = FhirEPI.from_dict(epi_data)
            result = epi.to_dict()
            
            assert isinstance(result, dict), "to_dict() returned non-dict"
            assert 'resourceType' in result, "to_dict() missing resourceType"
            assert 'entry' in result, "to_dict() missing entry"
            assert result['resourceType'] == 'Bundle', "Serialized resourceType incorrect"
            
            print(f"[PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_composition_retrieval(test_epis):
    """Test getting composition from all ePIs"""
    print("\n" + "=" * 70)
    print("TEST 4: Composition Resource Retrieval")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for name, epi_data in test_epis.items():
        try:
            epi = FhirEPI.from_dict(epi_data)
            comp = epi.get_composition()
            
            assert comp is not None, "get_composition() returned None"
            assert 'resourceType' in comp, "Composition missing resourceType"
            assert comp['resourceType'] == 'Composition', "Not a Composition resource"
            
            # Try to get title
            title = comp.get('title', 'N/A')
            print(f"[PASS] {name}: {title}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_preprocessing_logic(test_epis):
    """Test preprocessing logic (model-level)"""
    print("\n" + "=" * 70)
    print("TEST 5: Preprocessing Logic (Model-Level)")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    def apply_preprocessing(epi: FhirEPI) -> FhirEPI:
        """Simple preprocessing that preserves all data"""
        processed_epi = FhirEPI(
            resource_type=epi.resource_type,
            type=epi.type,
            timestamp=epi.timestamp,
            entry=epi.entry.copy() if epi.entry else [],
            meta=epi.meta,
            identifier=epi.identifier,
            signature=epi.signature
        )
        return processed_epi
    
    for name, epi_data in test_epis.items():
        try:
            # Load and preprocess
            epi = FhirEPI.from_dict(epi_data)
            processed = apply_preprocessing(epi)
            
            # Verify structure
            assert processed.resource_type == 'Bundle', "Preprocessing changed resourceType"
            assert processed.type == 'document', "Preprocessing changed type"
            assert len(processed.entry) == len(epi.entry), "Entry count changed"
            
            # Convert back
            result = processed.to_dict()
            assert isinstance(result, dict), "Result is not a dict"
            assert result['resourceType'] == 'Bundle', "Result is not a Bundle"
            
            print(f"[PASS] {name} ({len(processed.entry)} entries preserved)")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_resource_filtering(test_epis):
    """Test filtering entries by resource type"""
    print("\n" + "=" * 70)
    print("TEST 6: Resource Type Filtering")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for name, epi_data in test_epis.items():
        try:
            epi = FhirEPI.from_dict(epi_data)
            
            # Test filtering for Composition
            compositions = epi.get_entries_by_resource_type('Composition')
            assert len(compositions) >= 1, "No Composition entries found"
            
            # Verify structure
            for entry in compositions:
                assert 'resource' in entry, "Entry missing resource"
                assert entry['resource']['resourceType'] == 'Composition', "Not a Composition"
            
            # Count total resources
            total_types = {}
            for entry in epi.entry:
                if 'resource' in entry:
                    res_type = entry['resource'].get('resourceType', 'Unknown')
                    total_types[res_type] = total_types.get(res_type, 0) + 1
            
            types_str = ", ".join([f"{k}:{v}" for k, v in sorted(total_types.items())])
            print(f"[PASS] {name}: {types_str}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def print_summary(test_epis):
    """Print summary of all loaded ePIs"""
    print("\n" + "=" * 70)
    print("ePi SUMMARY")
    print("=" * 70)
    
    if not test_epis:
        print("No ePIs loaded!")
        return
    
    total_entries = 0
    resource_type_counts = {}
    
    for name, epi_data in test_epis.items():
        try:
            epi = FhirEPI.from_dict(epi_data)
            comp = epi.get_composition()
            title = comp.get('title', 'N/A') if comp else 'N/A'
            
            entry_count = len(epi.entry)
            total_entries += entry_count
            
            # Count resource types
            for entry in epi.entry:
                if 'resource' in entry:
                    res_type = entry['resource'].get('resourceType', 'Unknown')
                    resource_type_counts[res_type] = resource_type_counts.get(res_type, 0) + 1
            
            print(f"\n{name}")
            print(f"  Title: {title}")
            print(f"  Entries: {entry_count}")
            
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print(f"\n{'-' * 70}")
    print("RESOURCE TYPE DISTRIBUTION")
    print(f"{'-' * 70}")
    
    for res_type in sorted(resource_type_counts.keys()):
        count = resource_type_counts[res_type]
        print(f"  {res_type}: {count}")
    
    print(f"\nTotal entries across all ePIs: {total_entries}")
    print("=" * 70)


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("REAL ePi TEST SUITE")
    print("=" * 70)
    
    # Load test ePIs
    test_epis = load_test_epis()
    
    if not test_epis:
        print("ERROR: No test ePIs loaded!")
        return 1
    
    print(f"\nLoaded {len(test_epis)} test ePIs")
    
    # Run all tests
    results = []
    results.append(("Basic Structure", test_basic_structure(test_epis)))
    results.append(("Model Creation", test_model_creation(test_epis)))
    results.append(("Serialization", test_serialization(test_epis)))
    results.append(("Composition Retrieval", test_composition_retrieval(test_epis)))
    results.append(("Resource Filtering", test_resource_filtering(test_epis)))
    results.append(("Preprocessing Logic", test_preprocessing_logic(test_epis)))
    
    # Print summary
    print_summary(test_epis)
    
    # Print test results
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\nALL TESTS PASSED!")
        return 0
    else:
        print("\nSOME TESTS FAILED!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
