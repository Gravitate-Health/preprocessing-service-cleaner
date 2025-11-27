"""
HtmlElementLink Extension Manager

Provides functions to manage HtmlElementLink extensions in Composition resources.

Functions:
  - list_html_element_links(): List all HtmlElementLink extensions
  - get_html_element_link(): Get a specific extension by element class
  - add_html_element_link(): Add a new extension
  - remove_html_element_link(): Remove an extension by element class
  - remove_all_html_element_links(): Clear all extensions
"""

from typing import List, Optional, Dict, Any
from preprocessor.models.html_element_link import (
    HtmlElementLink,
    CodeableReference,
    Coding,
)


def list_html_element_links(composition: Dict[str, Any]) -> List[HtmlElementLink]:
    """
    List all HtmlElementLink extensions in a Composition resource

    Args:
        composition: Composition resource dictionary

    Returns:
        List of HtmlElementLink instances
    """
    links = []

    extensions = composition.get("extension", [])
    for ext in extensions:
        url = ext.get("url")
        if url == HtmlElementLink.STRUCTURE_DEFINITION_URL:
            link = HtmlElementLink.from_dict(ext)
            links.append(link)

    return links


def get_html_element_link(
    composition: Dict[str, Any], element_class: str
) -> Optional[HtmlElementLink]:
    """
    Get a specific HtmlElementLink extension by element class

    Args:
        composition: Composition resource dictionary
        element_class: The HTML element class to search for

    Returns:
        HtmlElementLink instance or None if not found
    """
    links = list_html_element_links(composition)
    for link in links:
        if link.element_class == element_class:
            return link
    return None


def add_html_element_link(
    composition: Dict[str, Any],
    element_class: str,
    concept: CodeableReference,
    replace_if_exists: bool = False,
) -> bool:
    """
    Add a new HtmlElementLink extension to a Composition

    Args:
        composition: Composition resource dictionary (modified in-place)
        element_class: The HTML element class to annotate
        concept: CodeableReference object with the clinical concept
        replace_if_exists: If True, replace existing extension with same element_class
                          If False, don't add if element_class already exists

    Returns:
        True if added, False if skipped (already exists and replace_if_exists=False)

    Raises:
        ValueError: If element_class or concept is invalid
    """
    if not element_class or not isinstance(element_class, str):
        raise ValueError("element_class must be a non-empty string")

    if not isinstance(concept, CodeableReference):
        raise ValueError("concept must be a CodeableReference instance")

    # Check if already exists
    existing = get_html_element_link(composition, element_class)
    if existing:
        if not replace_if_exists:
            return False
        # Remove the existing one first
        remove_html_element_link(composition, element_class)

    # Ensure extensions array exists
    if "extension" not in composition:
        composition["extension"] = []

    # Create and add the new extension
    new_link = HtmlElementLink(element_class=element_class, concept=concept)
    composition["extension"].append(new_link.to_dict())

    return True


def remove_html_element_link(
    composition: Dict[str, Any], element_class: str
) -> bool:
    """
    Remove a specific HtmlElementLink extension by element class

    Args:
        composition: Composition resource dictionary (modified in-place)
        element_class: The HTML element class to remove

    Returns:
        True if removed, False if not found
    """
    if "extension" not in composition:
        return False

    extensions = composition["extension"]
    initial_count = len(extensions)

    # Filter out matching extensions
    composition["extension"] = [
        ext
        for ext in extensions
        if not (
            ext.get("url") == HtmlElementLink.STRUCTURE_DEFINITION_URL
            and any(
                e.get("url") == "elementClass"
                and e.get("valueString") == element_class
                for e in ext.get("extension", [])
            )
        )
    ]

    return len(composition["extension"]) < initial_count


def remove_all_html_element_links(composition: Dict[str, Any]) -> int:
    """
    Remove all HtmlElementLink extensions from a Composition

    Args:
        composition: Composition resource dictionary (modified in-place)

    Returns:
        Number of extensions removed
    """
    if "extension" not in composition:
        return 0

    initial_count = len(list_html_element_links(composition))

    # Keep only non-HtmlElementLink extensions
    composition["extension"] = [
        ext
        for ext in composition.get("extension", [])
        if ext.get("url") != HtmlElementLink.STRUCTURE_DEFINITION_URL
    ]

    return initial_count


def filter_html_element_links(
    composition: Dict[str, Any],
    predicate=None,
) -> List[HtmlElementLink]:
    """
    Filter HtmlElementLink extensions by a predicate function

    Args:
        composition: Composition resource dictionary
        predicate: Function that takes HtmlElementLink and returns bool
                  If None, returns all links

    Returns:
        Filtered list of HtmlElementLink instances

    Examples:
        # Get all pregnancy-related annotations
        links = filter_html_element_links(comp, lambda l: "pregnancy" in l.element_class.lower())

        # Get all annotations for a specific concept system
        links = filter_html_element_links(comp, 
            lambda l: l.concept.codings[0].system == "http://snomed.info/sct" if l.concept.codings else False
        )
    """
    links = list_html_element_links(composition)

    if predicate is None:
        return links

    return [link for link in links if predicate(link)]


def get_element_classes(composition: Dict[str, Any]) -> List[str]:
    """
    Get list of all element classes in HtmlElementLink extensions

    Args:
        composition: Composition resource dictionary

    Returns:
        List of element class strings
    """
    links = list_html_element_links(composition)
    return [link.element_class for link in links if link.element_class]


def get_concepts_for_element_class(
    composition: Dict[str, Any], element_class: str
) -> List[Coding]:
    """
    Get all coding concepts for a specific element class

    Args:
        composition: Composition resource dictionary
        element_class: The HTML element class

    Returns:
        List of Coding instances for that element class
    """
    link = get_html_element_link(composition, element_class)
    if not link or not link.concept:
        return []
    return link.concept.codings
