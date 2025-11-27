#!/usr/bin/env python3
"""
Comprehensive test suite using real ePIs from the testing folder

Tests the FhirEPI model and preprocess controller with actual ePI documents
"""

import os
import json
import unittest
from pathlib import Path
from preprocessor.models.fhir_epi import FhirEPI
from preprocessor.controllers.preprocess_controller import preprocess_post


class TestRealEPIs(unittest.TestCase):
    """Test FhirEPI model with real ePI documents"""
    
    @classmethod
    def setUpClass(cls):
        """Load all test ePIs from the testing folder"""
        test_folder = Path(__file__).parent / "testing ePIs"
        cls.test_epis = {}
        cls.test_files = []
        
        if test_folder.exists():
            for json_file in sorted(test_folder.glob("*.json")):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        cls.test_epis[json_file.stem] = data
                        cls.test_files.append(json_file.name)
                except Exception as e:
                    print(f"Warning: Could not load {json_file.name}: {e}")
        
        cls.file_count = len(cls.test_epis)
    
    def test_epi_files_exist(self):
        """Verify test ePI files are loaded"""
        self.assertGreater(self.file_count, 0, 
                          "No test ePI files found in testing ePIs folder")
    
    def test_all_epis_are_valid_bundles(self):
        """Test that all test ePIs are valid FHIR Bundles"""
        for name, epi_data in self.test_epis.items():
            self.assertIn('resourceType', epi_data, 
                         f"{name} missing resourceType")
            self.assertEqual(epi_data['resourceType'], 'Bundle',
                           f"{name} is not a Bundle")
            self.assertIn('type', epi_data,
                         f"{name} missing type")
            self.assertEqual(epi_data['type'], 'document',
                           f"{name} is not a document bundle")
    
    def test_all_epis_have_entries(self):
        """Test that all ePIs have entry arrays"""
        for name, epi_data in self.test_epis.items():
            self.assertIn('entry', epi_data,
                         f"{name} missing entry array")
            self.assertIsInstance(epi_data['entry'], list,
                                 f"{name} entry is not a list")
            self.assertGreater(len(epi_data['entry']), 0,
                             f"{name} entry array is empty")
    
    def test_all_epis_create_model(self):
        """Test that all ePIs can be loaded into FhirEPI model"""
        for name, epi_data in self.test_epis.items():
            try:
                epi = FhirEPI.from_dict(epi_data)
                self.assertEqual(epi.resource_type, 'Bundle',
                               f"{name} model resourceType incorrect")
                self.assertEqual(epi.type, 'document',
                               f"{name} model type incorrect")
                self.assertIsNotNone(epi.entry,
                                   f"{name} model entry is None")
            except Exception as e:
                self.fail(f"{name} failed to create model: {e}")
    
    def test_all_epis_serialize_to_dict(self):
        """Test that all ePIs can be converted back to dict"""
        for name, epi_data in self.test_epis.items():
            try:
                epi = FhirEPI.from_dict(epi_data)
                result = epi.to_dict()
                self.assertIsInstance(result, dict,
                                    f"{name} to_dict() returned non-dict")
                self.assertIn('resourceType', result,
                            f"{name} to_dict() missing resourceType")
                self.assertIn('entry', result,
                            f"{name} to_dict() missing entry")
            except Exception as e:
                self.fail(f"{name} failed to serialize: {e}")
    
    def test_all_epis_have_composition(self):
        """Test that all ePIs have a Composition resource"""
        for name, epi_data in self.test_epis.items():
            epi = FhirEPI.from_dict(epi_data)
            comp = epi.get_composition()
            self.assertIsNotNone(comp,
                               f"{name} missing Composition resource")
            self.assertEqual(comp['resourceType'], 'Composition',
                           f"{name} first entry is not Composition")
    
    def test_all_epis_preprocess(self):
        """Test that all ePIs can be preprocessed"""
        for name, epi_data in self.test_epis.items():
            try:
                result, status_code = preprocess_post(epi_data)
                self.assertEqual(status_code, 200,
                               f"{name} preprocessing returned status {status_code}")
                self.assertIsInstance(result, dict,
                                    f"{name} preprocessing returned non-dict")
                self.assertIn('resourceType', result,
                            f"{name} preprocessed result missing resourceType")
            except Exception as e:
                self.fail(f"{name} preprocessing failed: {e}")
    
    def test_composition_title_extraction(self):
        """Test extracting composition titles from all ePIs"""
        for name, epi_data in self.test_epis.items():
            epi = FhirEPI.from_dict(epi_data)
            comp = epi.get_composition()
            if comp and 'title' in comp:
                title = comp['title']
                self.assertIsInstance(title, str,
                                    f"{name} title is not string")
                self.assertGreater(len(title), 0,
                                 f"{name} title is empty")
    
    def test_entry_filtering(self):
        """Test filtering entries by resource type"""
        for name, epi_data in self.test_epis.items():
            epi = FhirEPI.from_dict(epi_data)
            
            # Test Composition filtering
            compositions = epi.get_entries_by_resource_type('Composition')
            self.assertGreaterEqual(len(compositions), 1,
                                  f"{name} has no Composition entries")
            
            # All filtered entries should have the resource field
            for entry in compositions:
                self.assertIn('resource', entry,
                            f"{name} Composition entry missing resource")
                self.assertEqual(entry['resource']['resourceType'], 'Composition',
                               f"{name} filtered entry is not Composition")
    
    def test_metadata_preservation(self):
        """Test that metadata is preserved through serialization"""
        for name, epi_data in self.test_epis.items():
            epi = FhirEPI.from_dict(epi_data)
            result = epi.to_dict()
            
            # Check identifier preservation
            if 'identifier' in epi_data:
                self.assertIn('identifier', result,
                            f"{name} identifier not preserved")
            
            # Check timestamp preservation
            if 'timestamp' in epi_data:
                self.assertIn('timestamp', result,
                            f"{name} timestamp not preserved")
                self.assertEqual(epi_data['timestamp'], result['timestamp'],
                               f"{name} timestamp value changed")


class TestEPISummary(unittest.TestCase):
    """Generate summary statistics about test ePIs"""
    
    def test_print_epi_summary(self):
        """Print summary of all loaded ePIs"""
        test_folder = Path(__file__).parent / "testing ePIs"
        
        if not test_folder.exists():
            self.skipTest("testing ePIs folder not found")
        
        print("\n" + "=" * 70)
        print("REAL ePi TEST SUMMARY")
        print("=" * 70)
        
        total_entries = 0
        resource_type_counts = {}
        
        for json_file in sorted(test_folder.glob("*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Get file name and size
                    file_size = json_file.stat().st_size / 1024  # KB
                    
                    # Parse as ePI
                    epi = FhirEPI.from_dict(data)
                    comp = epi.get_composition()
                    title = comp.get('title', 'N/A') if comp else 'N/A'
                    
                    # Count entries and resource types
                    entry_count = len(epi.entry)
                    total_entries += entry_count
                    
                    # Count resource types
                    for entry in epi.entry:
                        if 'resource' in entry:
                            res_type = entry['resource'].get('resourceType', 'Unknown')
                            resource_type_counts[res_type] = resource_type_counts.get(res_type, 0) + 1
                    
                    print(f"\n[{json_file.stem}]")
                    print(f"  File size: {file_size:.1f} KB")
                    print(f"  Title: {title}")
                    print(f"  Entries: {entry_count}")
                    
            except Exception as e:
                print(f"\n[{json_file.stem}] ERROR: {e}")
        
        print(f"\n{'-' * 70}")
        print("RESOURCE TYPE DISTRIBUTION")
        print(f"{'-' * 70}")
        
        for res_type in sorted(resource_type_counts.keys()):
            count = resource_type_counts[res_type]
            print(f"  {res_type}: {count}")
        
        print(f"\nTotal entries across all ePIs: {total_entries}")
        print("=" * 70 + "\n")


if __name__ == '__main__':
    unittest.main(verbosity=2)
