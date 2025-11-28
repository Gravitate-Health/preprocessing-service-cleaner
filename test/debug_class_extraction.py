"""
Debug script to test class extraction from Karvea ePI
"""

import json
import sys
from pathlib import Path

# Add preprocessor to path
sys.path.insert(0, str(Path(__file__).parent))

from preprocessor.models.html_content_manager import get_html_content
from preprocessor.models.html_optimizer import extract_html_classes, optimize_html
from preprocessor.models.html_element_link_manager import get_element_classes, list_html_element_links


def main():
    # Load the test ePI
    test_file = Path(__file__).parent / "preprocessor/test/testing ePIs/Bundle-Processedbundlekarvea.json"
    
    print(f"Loading: {test_file}")
    with open(test_file, 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    
    # Find the Composition
    composition = None
    for entry in bundle.get('entry', []):
        resource = entry.get('resource', {})
        if resource.get('resourceType') == 'Composition':
            composition = resource
            break
    
    if not composition:
        print("ERROR: No Composition found!")
        return
    
    print("\n" + "="*80)
    print("STEP 1: Check HtmlElementLink extensions")
    print("="*80)
    
    links = list_html_element_links(composition)
    element_classes = get_element_classes(composition)
    
    print(f"Number of HtmlElementLink extensions: {len(links)}")
    print(f"Element classes from extensions: {element_classes}")
    
    print("\n" + "="*80)
    print("STEP 2: Check Composition text.div HTML")
    print("="*80)
    
    html_content = get_html_content(composition)
    raw_html = html_content.raw_html
    
    print(f"Raw HTML length: {len(raw_html)} characters")
    print(f"\nChecking for class presence in raw HTML:")
    for cls in element_classes:
        present = cls in raw_html
        print(f"  - {cls}: {present}")
        if present:
            # Show context
            idx = raw_html.find(cls)
            snippet = raw_html[max(0, idx-50):idx+50]
            print(f"    Context: ...{snippet}...")
    
    print("\n" + "="*80)
    print("STEP 3: Extract classes from raw HTML")
    print("="*80)
    
    extracted_classes = extract_html_classes(raw_html)
    print(f"Extracted classes: {extracted_classes}")
    
    print("\n" + "="*80)
    print("STEP 4: Check sections")
    print("="*80)
    
    sections = composition.get('section', [])
    print(f"Number of sections: {len(sections)}")
    
    for i, section in enumerate(sections):
        section_html = section.get('text', {}).get('div', '')
        if section_html:
            section_classes = extract_html_classes(section_html)
            print(f"\nSection {i} ('{section.get('title', 'N/A')}'):")
            print(f"  HTML length: {len(section_html)} characters")
            print(f"  Classes: {section_classes}")
            
            # Check for our target classes
            for cls in element_classes:
                if cls in section_html:
                    print(f"  - Found '{cls}' in this section!")
    
    print("\n" + "="*80)
    print("STEP 5: Test optimization")
    print("="*80)
    
    optimized_html = optimize_html(raw_html)
    print(f"Optimized HTML length: {len(optimized_html)} characters")
    
    optimized_classes = extract_html_classes(optimized_html)
    print(f"Classes after optimization: {optimized_classes}")
    
    print("\nClass comparison:")
    print(f"  Before: {extracted_classes}")
    print(f"  After:  {optimized_classes}")
    print(f"  Lost:   {extracted_classes - optimized_classes}")
    print(f"  Gained: {optimized_classes - extracted_classes}")
    
    # Check if important classes are preserved
    print("\nImportant class preservation:")
    for cls in element_classes:
        before = cls in extracted_classes
        after = cls in optimized_classes
        status = "✓ PRESERVED" if (before and after) else ("✗ LOST" if before else "✗ NOT FOUND")
        print(f"  {cls}: {status}")


if __name__ == '__main__':
    main()
