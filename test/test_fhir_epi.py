"""
Unit tests for the preprocess controller and FHIR ePI model
"""

import unittest
import json
from preprocessor.models.fhir_epi import FhirEPI
from preprocessor.controllers.preprocess_controller import preprocess_post


class TestFhirEPI(unittest.TestCase):
    """Test FHIR ePI model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_bundle = {
            "resourceType": "Bundle",
            "type": "document",
            "timestamp": "2024-01-15T10:30:00Z",
            "identifier": {
                "system": "http://example.com/epi",
                "value": "epi-001"
            },
            "entry": [
                {
                    "resource": {
                        "resourceType": "Composition",
                        "id": "comp-001",
                        "status": "final",
                        "type": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "51725-0",
                                "display": "Imprint labeling (Medication Guide)"
                            }]
                        },
                        "subject": {
                            "reference": "Medication/med-001"
                        }
                    }
                },
                {
                    "resource": {
                        "resourceType": "Medication",
                        "id": "med-001",
                        "code": {
                            "coding": [{
                                "system": "http://www.whocc.no/atc",
                                "code": "N02BA01",
                                "display": "Aspirin"
                            }]
                        }
                    }
                }
            ]
        }
    
    def test_fhir_epi_from_dict(self):
        """Test creating FhirEPI from dictionary"""
        epi = FhirEPI.from_dict(self.sample_bundle)
        
        self.assertEqual(epi.resource_type, "Bundle")
        self.assertEqual(epi.type, "document")
        self.assertEqual(epi.timestamp, "2024-01-15T10:30:00Z")
        self.assertEqual(len(epi.entry), 2)
        self.assertIsNotNone(epi.identifier)
    
    def test_fhir_epi_to_dict(self):
        """Test converting FhirEPI to dictionary"""
        epi = FhirEPI.from_dict(self.sample_bundle)
        result = epi.to_dict()
        
        self.assertEqual(result["resourceType"], "Bundle")
        self.assertEqual(result["type"], "document")
        self.assertEqual(result["timestamp"], "2024-01-15T10:30:00Z")
        self.assertEqual(len(result["entry"]), 2)
    
    def test_fhir_epi_get_composition(self):
        """Test retrieving Composition resource from bundle"""
        epi = FhirEPI.from_dict(self.sample_bundle)
        composition = epi.get_composition()
        
        self.assertIsNotNone(composition)
        self.assertEqual(composition["resourceType"], "Composition")
        self.assertEqual(composition["id"], "comp-001")
    
    def test_fhir_epi_get_entries_by_type(self):
        """Test filtering entries by resource type"""
        epi = FhirEPI.from_dict(self.sample_bundle)
        medications = epi.get_entries_by_resource_type("Medication")
        
        self.assertEqual(len(medications), 1)
        self.assertEqual(medications[0]["resource"]["resourceType"], "Medication")
    
    def test_fhir_epi_empty_entries(self):
        """Test FhirEPI with empty entries"""
        epi = FhirEPI()
        result = epi.to_dict()
        
        self.assertEqual(result["resourceType"], "Bundle")
        self.assertEqual(result["type"], "document")
        # Empty entries list should not be included
        self.assertNotIn("entry", result)


class TestPreprocessController(unittest.TestCase):
    """Test preprocess controller"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_bundle = {
            "resourceType": "Bundle",
            "type": "document",
            "timestamp": "2024-01-15T10:30:00Z",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Composition",
                        "id": "comp-001",
                        "status": "final"
                    }
                }
            ]
        }
    
    def test_preprocess_valid_epi(self):
        """Test preprocessing a valid ePI"""
        result, status_code = preprocess_post(self.sample_bundle)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(result["resourceType"], "Bundle")
        self.assertEqual(result["type"], "document")
    
    def test_preprocess_none_body(self):
        """Test preprocessing with None body"""
        result, status_code = preprocess_post(None)
        
        self.assertEqual(status_code, 400)
        self.assertIn("error", result)
    
    def test_preprocess_invalid_resource_type(self):
        """Test preprocessing with invalid resourceType"""
        invalid_bundle = self.sample_bundle.copy()
        invalid_bundle["resourceType"] = "Patient"
        
        result, status_code = preprocess_post(invalid_bundle)
        
        self.assertEqual(status_code, 400)
        self.assertIn("error", result)
        self.assertIn("Bundle", result["error"])
    
    def test_preprocess_invalid_bundle_type(self):
        """Test preprocessing with invalid bundle type"""
        invalid_bundle = self.sample_bundle.copy()
        invalid_bundle["type"] = "collection"
        
        result, status_code = preprocess_post(invalid_bundle)
        
        self.assertEqual(status_code, 400)
        self.assertIn("error", result)
        self.assertIn("document", result["error"])
    
    def test_preprocess_preserves_data(self):
        """Test that preprocessing preserves the ePI data"""
        result, status_code = preprocess_post(self.sample_bundle)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(result["timestamp"], self.sample_bundle["timestamp"])
        self.assertEqual(len(result["entry"]), len(self.sample_bundle["entry"]))


if __name__ == '__main__':
    unittest.main()
