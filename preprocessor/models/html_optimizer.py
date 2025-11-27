"""
HTML Optimizer for FHIR ePI content

This module provides functions to optimize HTML content by:
- Removing non-functional tags (empty spans, divs without attributes)
- Simplifying nested tags with mergeable attributes
- Preserving content integrity
"""

from bs4 import BeautifulSoup, NavigableString, Tag
from typing import Set, List, Optional
import re


def optimize_html(html: str) -> str:
    """
    Optimize HTML by removing non-functional tags and simplifying nested structures.
    
    Args:
        html: Raw HTML string (typically from Composition.text.div)
    
    Returns:
        Optimized HTML string
    """
    if not html or not html.strip():
        return html
    
    # Parse with lxml for better performance and handling
    soup = BeautifulSoup(html, 'lxml')
    
    # Remove non-functional tags
    _remove_empty_tags(soup)
    
    # Simplify nested tags
    _simplify_nested_tags(soup)
    
    # Get the body content (lxml adds html/body wrapper)
    if soup.body:
        # Return inner HTML of body
        return ''.join(str(child) for child in soup.body.children)
    
    return str(soup)


def extract_html_classes(html: str) -> Set[str]:
    """
    Extract all unique CSS class names used in the HTML content.
    
    Args:
        html: HTML string to analyze
    
    Returns:
        Set of class names found in the HTML
    """
    if not html or not html.strip():
        return set()
    
    soup = BeautifulSoup(html, 'lxml')
    classes = set()
    
    for tag in soup.find_all(True):  # Find all tags
        if tag.get('class'):
            # class attribute is a list in BeautifulSoup
            classes.update(tag.get('class'))
    
    return classes


def _remove_empty_tags(soup: BeautifulSoup) -> None:
    """
    Remove tags that have no functional purpose:
    - Empty tags with no content
    - Tags with no attributes and no meaningful content
    - Self-closing tags that are empty
    
    Modifies soup in place.
    """
    # Tags that are commonly non-functional when empty
    removable_tags = ['span', 'div', 'p', 'em', 'strong', 'i', 'b', 'u']
    
    changed = True
    while changed:
        changed = False
        for tag_name in removable_tags:
            for tag in soup.find_all(tag_name):
                # Check if tag has any attributes
                has_attributes = bool(tag.attrs)
                
                # Check if tag has meaningful content
                text_content = tag.get_text(strip=True)
                has_content = bool(text_content)
                
                # Check if tag has child tags
                has_children = bool(tag.find_all(True))
                
                # Remove if: no attributes AND (no content OR only whitespace children)
                if not has_attributes and not has_content and not has_children:
                    tag.decompose()
                    changed = True


def _simplify_nested_tags(soup: BeautifulSoup) -> None:
    """
    Simplify nested tags of the same type by merging attributes.
    
    Example: <p class="c1"><p class="c2">hello</p></p> -> <p class="c1 c2">hello</p>
    
    Modifies soup in place.
    """
    # Tags that can be simplified when nested
    simplifiable_tags = ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    
    changed = True
    iterations = 0
    max_iterations = 10  # Prevent infinite loops
    
    while changed and iterations < max_iterations:
        changed = False
        iterations += 1
        
        for tag_name in simplifiable_tags:
            for outer_tag in soup.find_all(tag_name):
                # Check if this tag has exactly one child that is the same tag type
                children = list(outer_tag.children)
                
                # Filter out pure whitespace text nodes
                non_whitespace_children = [
                    child for child in children 
                    if not (isinstance(child, NavigableString) and not child.strip())
                ]
                
                if len(non_whitespace_children) == 1:
                    inner_child = non_whitespace_children[0]
                    
                    # Check if the single child is a tag of the same type
                    if isinstance(inner_child, Tag) and inner_child.name == tag_name:
                        # Merge attributes from outer to inner
                        _merge_tag_attributes(outer_tag, inner_child)
                        
                        # Replace outer tag with inner tag
                        outer_tag.replace_with(inner_child)
                        changed = True
                        break  # Restart search after modification

            # Second pass: merge empty tag followed by same-type sibling
            for tag in soup.find_all(tag_name):
                # Determine if current tag is effectively empty
                has_child_tags = bool(tag.find_all(True))
                text_content = tag.get_text(strip=True)
                is_effectively_empty = (not has_child_tags and not text_content)

                next_sib = tag.next_sibling
                # Skip whitespace siblings
                while isinstance(next_sib, NavigableString) and not next_sib.strip():
                    next_sib = next_sib.next_sibling

                if is_effectively_empty and isinstance(next_sib, Tag) and next_sib.name == tag_name:
                    # Merge attributes/classes from current empty tag into next sibling then remove current
                    _merge_tag_attributes(tag, next_sib)
                    tag.decompose()
                    changed = True
                    break


def _merge_tag_attributes(outer_tag: Tag, inner_tag: Tag) -> None:
    """
    Merge attributes from outer tag into inner tag.
    
    Special handling for class attributes (combine them).
    For other attributes, inner tag takes precedence.
    """
    for attr_name, attr_value in outer_tag.attrs.items():
        if attr_name == 'class':
            # Combine class lists
            outer_classes = set(attr_value) if isinstance(attr_value, list) else {attr_value}
            inner_classes = set(inner_tag.get('class', []))
            combined_classes = list(outer_classes | inner_classes)
            inner_tag['class'] = combined_classes
        elif attr_name not in inner_tag.attrs:
            # Only add attribute if inner doesn't have it (inner takes precedence)
            inner_tag[attr_name] = attr_value


def validate_content_integrity(original_html: str, optimized_html: str) -> bool:
    """
    Validate that optimization preserved the text content.
    
    Args:
        original_html: Original HTML string
        optimized_html: Optimized HTML string
    
    Returns:
        True if text content is preserved, False otherwise
    """
    if not original_html and not optimized_html:
        return True
    
    soup_original = BeautifulSoup(original_html, 'lxml')
    soup_optimized = BeautifulSoup(optimized_html, 'lxml')
    
    text_original = soup_original.get_text(strip=True)
    text_optimized = soup_optimized.get_text(strip=True)
    
    return text_original == text_optimized
