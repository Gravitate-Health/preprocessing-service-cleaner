#!/usr/bin/env python3
"""
Debug script to understand why the 'liver' class is being removed from Dovato ePI
"""

import json
from pathlib import Path
from preprocessor.models.fhir_epi import FhirEPI
from preprocessor.models.html_content_manager import get_html_content
from preprocessor.models.html_optimizer import extract_html_classes
from preprocessor.models.html_element_link_manager import get_element_classes
from preprocessor.controllers.preprocess_controller import _collect_all_html_classes_from_resource

# Load the Dovato ePI
TEST_EPI_DIR = Path(__file__).parent / "testing ePIs"
dovato_file = TEST_EPI_DIR / "Bundle-processedbundledovato-en.json"

with open(dovato_file, 'r', encoding='utf-8') as f:
    dovato_bundle = json.load(f)

print("=== DEBUGGING DOVATO LIVER CLASS ISSUE ===\n")

# Get the Composition
composition = None
for entry in dovato_bundle.get('entry', []):
    resource = entry.get('resource', {})
    if resource.get('resourceType') == 'Composition':
        composition = resource
        break

if not composition:
    print("ERROR: No Composition found")
    exit(1)

# 1. Check what classes are in the HtmlElementLink extensions
print("1. Classes defined in HtmlElementLink extensions:")
extension_classes = get_element_classes(composition)
print(f"   {extension_classes}")
print(f"   'liver' in extensions: {'liver' in extension_classes}\n")

# 2. Check the composition text.div HTML
print("2. Classes in Composition.text.div:")
comp_html = get_html_content(composition)
if comp_html and not comp_html.is_empty:
    comp_classes = extract_html_classes(comp_html.raw_html)
    print(f"   {comp_classes}")
    print(f"   'liver' in Composition.text.div: {'liver' in comp_classes}")
    print(f"   Raw HTML contains 'liver': {'liver' in comp_html.raw_html}\n")
else:
    print("   No HTML in Composition.text.div\n")

# 3. Check each section's HTML
print("3. Checking sections for 'liver' class:")
sections = composition.get('section', [])
print(f"   Total sections: {len(sections)}\n")

def check_sections_for_liver(sections, level=0):
    """Recursively check sections for liver class"""
    indent = "   " * (level + 1)
    for i, section in enumerate(sections):
        title = section.get('title', f'Section {i}')
        section_html = get_html_content(section)
        
        if section_html and not section_html.is_empty:
            section_classes = extract_html_classes(section_html.raw_html)
            has_liver_class = 'liver' in section_classes
            has_liver_text = 'liver' in section_html.raw_html.lower()
            
            print(f"{indent}Section: {title}")
            print(f"{indent}  Has 'liver' class: {has_liver_class}")
            print(f"{indent}  Contains 'liver' text: {has_liver_text}")
            
            if has_liver_class:
                print(f"{indent}  ✓ FOUND 'liver' class in section!")
                # Show snippet
                start = section_html.raw_html.find('class="liver"')
                if start != -1:
                    snippet = section_html.raw_html[max(0, start-50):start+100]
                    print(f"{indent}  Snippet: ...{snippet}...\n")
            
        # Check subsections
        if 'section' in section:
            check_sections_for_liver(section['section'], level + 1)

check_sections_for_liver(sections)

# 4. Use the actual preprocessing collection method
print("\n4. Using _collect_all_html_classes_from_resource():")
all_classes = _collect_all_html_classes_from_resource(composition)
print(f"   All classes collected: {all_classes}")
print(f"   'liver' in collected classes: {'liver' in all_classes}")

# 5. Summary
print("\n=== SUMMARY ===")
print(f"HtmlElementLink extensions define 'liver': {'liver' in extension_classes}")
print(f"_collect_all_html_classes_from_resource() finds 'liver': {'liver' in all_classes}")
print(f"\nExpected behavior: 'liver' should NOT be removed")
print(f"Issue: If 'liver' is being removed, it means the class collection is not finding it in the HTML")
