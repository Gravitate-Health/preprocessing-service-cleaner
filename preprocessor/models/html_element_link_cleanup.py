"""
HtmlElementLink Cleanup Utilities

Functions to remove unused HtmlElementLink extensions from Composition resources
based on actual HTML class usage.
"""

from typing import Set, List, Dict, Any
from preprocessor.models.html_element_link_manager import (
    list_html_element_links,
    remove_html_element_link,
    get_element_classes
)
from preprocessor.models.html_optimizer import extract_html_classes


def cleanup_unused_html_element_links(composition: Dict[str, Any], html_classes: Set[str]) -> Dict[str, int]:
    """
    Remove HtmlElementLink extensions that reference classes not present in the HTML.
    
    Args:
        composition: FHIR Composition resource dictionary
        html_classes: Set of class names actually used in the HTML content
    
    Returns:
        Dictionary with cleanup statistics:
        - 'total': Total number of HtmlElementLink extensions found
        - 'removed': Number of extensions removed
        - 'kept': Number of extensions kept
    """
    stats = {
        'total': 0,
        'removed': 0,
        'kept': 0
    }
    
    # Get all HtmlElementLink extensions
    all_links = list_html_element_links(composition)
    stats['total'] = len(all_links)
    
    if not all_links:
        return stats
    
    # Get all element classes from extensions
    extension_classes = get_element_classes(composition)
    print(f"Found {stats['total']} HtmlElementLink extensions.")
    print(f"Extension classes: {extension_classes}")
    print(f"HTML classes: {html_classes}")
    
    # Identify which classes are not used in HTML
    unused_classes = extension_classes - html_classes
    print(f"Unused classes: {unused_classes}")
    
    # Remove extensions for unused classes
    for element_class in unused_classes:
        try:
            remove_html_element_link(composition, element_class)
            stats['removed'] += 1
        except Exception as e:
            # Log but continue if removal fails
            print(f"Warning: Failed to remove HtmlElementLink for class '{element_class}': {e}")
    
    stats['kept'] = stats['total'] - stats['removed']
    
    return stats


def analyze_html_element_link_usage(composition: Dict[str, Any], html_content: str) -> Dict[str, Any]:
    """
    Analyze which HtmlElementLink extensions are used vs unused.
    
    Args:
        composition: FHIR Composition resource dictionary
        html_content: HTML content string from composition.text.div
    
    Returns:
        Dictionary with analysis results:
        - 'html_classes': Set of classes found in HTML
        - 'extension_classes': Set of classes in HtmlElementLink extensions
        - 'used_classes': Classes that appear in both HTML and extensions
        - 'unused_extension_classes': Classes in extensions but not in HTML
        - 'unlinked_html_classes': Classes in HTML but not in extensions
    """
    html_classes = extract_html_classes(html_content)
    extension_classes = get_element_classes(composition)
    
    return {
        'html_classes': html_classes,
        'extension_classes': extension_classes,
        'used_classes': html_classes & extension_classes,
        'unused_extension_classes': extension_classes - html_classes,
        'unlinked_html_classes': html_classes - extension_classes
    }
