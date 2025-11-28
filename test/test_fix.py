"""
Test script to verify the fix for subsection HTML processing
"""

import json
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from preprocessor.models.html_content_manager import get_html_content
from preprocessor.models.html_optimizer import extract_html_classes


def collect_all_html_classes_from_resource(resource):
    """Collect all CSS classes from a resource and all its sections/subsections"""
    all_classes = set()
    
    # Get classes from resource text.div
    html_content = get_html_content(resource)
    if html_content and not html_content.is_empty:
        all_classes.update(extract_html_classes(html_content.raw_html))
        print(f"Classes from resource text.div: {extract_html_classes(html_content.raw_html)}")
    
    # Recursively get classes from sections
    def collect_from_sections(sections, level=0):
        classes = set()
        for section in sections:
            title = section.get('title', 'N/A')
            # Get classes from section text.div
            section_html = get_html_content(section)
            if section_html and not section_html.is_empty:
                section_classes = extract_html_classes(section_html.raw_html)
                if section_classes:
                    print(f"{'  '*level}Section '{title}': {section_classes}")
                classes.update(section_classes)
            
            # Process subsections
            if 'section' in section:
                classes.update(collect_from_sections(section['section'], level+1))
        return classes
    
    if 'section' in resource:
        print("Classes from sections:")
        all_classes.update(collect_from_sections(resource['section']))
    
    return all_classes


def main():
    # Load test ePI
    test_file = Path(__file__).parent / "testing ePIs/Bundle-Processedbundlekarvea.json"
    
    with open(test_file, 'r') as f:
        bundle = json.load(f)
    
    # Find Composition
    composition = None
    for entry in bundle.get('entry', []):
        resource = entry.get('resource', {})
        if resource.get('resourceType') == 'Composition':
            composition = resource
            break
    
    if not composition:
        print("ERROR: No Composition found!")
        return
    
    print("="*80)
    print("TESTING CLASS COLLECTION FROM ALL SECTIONS")
    print("="*80)
    
    all_classes = collect_all_html_classes_from_resource(composition)
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"Total classes found: {len(all_classes)}")
    print(f"Classes: {all_classes}")
    
    # Check for important classes
    important_classes = {'pregnancyCategory', 'breastfeedingCategory', 'lactose', 
                        'contra-indication-pregnancy', 'contra-indication-kidney',
                        'contra-indication-diabetes-mellitus'}
    
    print("\n" + "="*80)
    print("IMPORTANT CLASS CHECK")
    print("="*80)
    
    for cls in important_classes:
        if cls in all_classes:
            print(f"✓ {cls}: FOUND")
        else:
            print(f"✗ {cls}: NOT FOUND")


if __name__ == '__main__':
    main()
