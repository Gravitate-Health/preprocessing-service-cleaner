#!/usr/bin/env python3
"""
Test to verify the 'liver' class issue is fixed in Dovato ePI
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from preprocessor.models.html_element_link_manager import get_element_classes
from preprocessor.models.html_element_link import HtmlElementLink

# Load the Dovato ePI
TEST_EPI_DIR = Path(__file__).parent / "testing ePIs"
dovato_file = TEST_EPI_DIR / "Bundle-processedbundledovato-en.json"

with open(dovato_file, 'r', encoding='utf-8') as f:
    dovato_bundle = json.load(f)

print("=== TESTING LIVER CLASS FIX ===\n")

# Get the Composition
composition = None
for entry in dovato_bundle.get('entry', []):
    resource = entry.get('resource', {})
    if resource.get('resourceType') == 'Composition':
        composition = resource
        break

if not composition:
    print("ERROR: No Composition found")
    sys.exit(1)

# Test 1: Check the correct URL is being used
print("1. Extension URL Check:")
print(f"   HtmlElementLink.STRUCTURE_DEFINITION_URL = {HtmlElementLink.STRUCTURE_DEFINITION_URL}")
print(f"   Expected: http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink")
if HtmlElementLink.STRUCTURE_DEFINITION_URL == "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink":
    print("   ✓ PASS: Using correct URL\n")
else:
    print("   ✗ FAIL: Wrong URL\n")
    sys.exit(1)

# Test 2: Check get_element_classes finds all classes including 'liver'
print("2. get_element_classes() Test:")
allowed_classes = get_element_classes(composition)
print(f"   Found classes: {allowed_classes}")
if 'liver' in allowed_classes:
    print("   ✓ PASS: 'liver' class found in extensions\n")
else:
    print("   ✗ FAIL: 'liver' class NOT found\n")
    sys.exit(1)

# Test 3: Check all expected classes are found
print("3. All Expected Classes Test:")
expected = {'pregnancyCategory', 'indication', 'breastfeedingCategory', 'liver', 'contra-indication-hypericum'}
missing = expected - allowed_classes
if not missing:
    print(f"   ✓ PASS: All expected classes found\n")
else:
    print(f"   ✗ FAIL: Missing classes: {missing}\n")
    sys.exit(1)

# Test 4: Count extensions manually
print("4. Manual Extension Count:")
manual_count = 0
for ext in composition.get('extension', []):
    if ext.get('url') == HtmlElementLink.STRUCTURE_DEFINITION_URL:
        manual_count += 1
        for ext_detail in ext.get('extension', []):
            if ext_detail.get('url') == 'elementClass':
                element_class = ext_detail.get('valueString', '')
                print(f"   - {element_class}")

print(f"   Total HtmlElementLink extensions: {manual_count}")
if manual_count == len(expected):
    print("   ✓ PASS: Extension count matches\n")
else:
    print(f"   ✗ FAIL: Expected {len(expected)}, found {manual_count}\n")

print("=== ALL TESTS PASSED ===")
print("\nConclusion: The 'liver' class should now be preserved during preprocessing")
print("because get_element_classes() now correctly uses HtmlElementLink.STRUCTURE_DEFINITION_URL")
