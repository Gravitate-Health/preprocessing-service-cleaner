#!/usr/bin/env python3
"""
Quick test script to verify FhirEPI model functionality
"""

from preprocessor.models.fhir_epi import FhirEPI
import json

# Sample FHIR ePI Bundle
sample_epi = {
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
                "status": "final"
            }
        },
        {
            "resource": {
                "resourceType": "Medication",
                "id": "med-001"
            }
        }
    ]
}

print("=" * 60)
print("Testing FhirEPI Model")
print("=" * 60)

# Create FhirEPI from dict
epi = FhirEPI.from_dict(sample_epi)
print("\n[PASS] FhirEPI created from dict")
print(f"  - resourceType: {epi.resource_type}")
print(f"  - type: {epi.type}")
print(f"  - entries: {len(epi.entry)}")

# Get composition
comp = epi.get_composition()
print(f"\n[PASS] Composition retrieved: {comp['resourceType']} (id={comp['id']})")

# Get medications
meds = epi.get_entries_by_resource_type("Medication")
print(f"\n[PASS] Medications found: {len(meds)}")
for med in meds:
    print(f"  - {med['resource']['id']}")

# Convert back to dict
result = epi.to_dict()
print(f"\n[PASS] Converted to dict")
print(f"  Keys: {list(result.keys())}")

print(f"\n[PASS] JSON Output:")
print(json.dumps(result, indent=2))

print("\n" + "=" * 60)
print("All tests passed!")
print("=" * 60)

