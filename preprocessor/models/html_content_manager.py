"""
HTML Content Manager for ePI Composition Resources

Provides functions to extract, parse, modify, and manage HTML content
in ePI Composition resources.

The HTML content is typically stored in:
  composition['text']['div']

It contains XHTML markup representing the rendered ePI document.
"""

from typing import Dict, Any, List, Optional, Tuple
from html.parser import HTMLParser
import re


class HtmlContent:
    """
    Represents HTML content from a Composition's text.div field.
    
    Attributes:
        raw_html (str): The original XHTML string
        parsed (bool): Whether content has been parsed
    """
    
    def __init__(self, raw_html: str = ""):
        """Initialize with raw HTML content"""
        self.raw_html = raw_html
        self.parsed = False
    
    @classmethod
    def from_composition(cls, composition: Dict[str, Any]) -> "HtmlContent":
        """Create from Composition resource"""
        html = composition.get("text", {}).get("div", "")
        return cls(html)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to FHIR text structure"""
        return {
            "status": "extensions",
            "div": self.raw_html
        }
    
    @property
    def is_empty(self) -> bool:
        """Check if content is empty"""
        return not self.raw_html or len(self.raw_html.strip()) == 0
    
    @property
    def length(self) -> int:
        """Get HTML string length"""
        return len(self.raw_html)
    
    def __repr__(self):
        preview = self.raw_html[:50].replace("\n", " ") + "..."
        return f"HtmlContent(length={self.length}, preview={preview})"


class HtmlSection:
    """
    Represents a logical section of HTML content.
    
    A section is identified by its starting tag and contains
    all content until the next sibling or closing tag.
    
    Attributes:
        tag_name (str): HTML tag name (e.g., 'div', 'section', 'article')
        start_pos (int): Starting position in raw HTML
        end_pos (int): Ending position in raw HTML
        class_name (str): HTML class attribute if present
        id_attr (str): HTML id attribute if present
        content (str): The HTML content of this section
    """
    
    def __init__(
        self,
        tag_name: str,
        start_pos: int,
        end_pos: int,
        class_name: str = "",
        id_attr: str = "",
        content: str = ""
    ):
        self.tag_name = tag_name
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.class_name = class_name
        self.id_attr = id_attr
        self.content = content
    
    @property
    def length(self) -> int:
        """Get section length"""
        return self.end_pos - self.start_pos
    
    def __repr__(self):
        class_str = f".{self.class_name}" if self.class_name else ""
        id_str = f"#{self.id_attr}" if self.id_attr else ""
        return f"HtmlSection(<{self.tag_name}{id_str}{class_str}> @ {self.start_pos}..{self.end_pos})"


class HtmlElement:
    """
    Represents an individual HTML element with reference information.
    
    Attributes:
        tag (str): Tag name (e.g., 'p', 'div', 'h1')
        class_names (List[str]): CSS classes
        id (str): Element ID
        text_content (str): Text within element
        position (Tuple[int, int]): (start, end) position in raw HTML
        attributes (Dict[str, str]): Other attributes
    """
    
    def __init__(
        self,
        tag: str,
        text_content: str = "",
        class_names: List[str] = None,
        id: str = "",
        position: Tuple[int, int] = (0, 0),
        attributes: Dict[str, str] = None
    ):
        self.tag = tag
        self.text_content = text_content
        self.class_names = class_names or []
        self.id = id
        self.position = position
        self.attributes = attributes or {}
    
    def has_class(self, class_name: str) -> bool:
        """Check if element has a specific class"""
        return class_name in self.class_names
    
    def get_attribute(self, attr_name: str) -> Optional[str]:
        """Get attribute value"""
        return self.attributes.get(attr_name)
    
    def __repr__(self):
        class_str = f".{'.'.join(self.class_names)}" if self.class_names else ""
        id_str = f"#{self.id}" if self.id else ""
        return f"<{self.tag}{id_str}{class_str}>"


def get_html_content(composition: Dict[str, Any]) -> HtmlContent:
    """
    Extract HTML content from Composition resource
    
    Args:
        composition: Composition resource dictionary
    
    Returns:
        HtmlContent instance
    """
    return HtmlContent.from_composition(composition)


def update_html_content(
    composition: Dict[str, Any],
    new_content: str
) -> bool:
    """
    Update HTML content in Composition
    
    Args:
        composition: Composition resource (modified in-place)
        new_content: New HTML string
    
    Returns:
        True if updated successfully
    
    Raises:
        ValueError: If new_content is invalid
    """
    if not isinstance(new_content, str):
        raise ValueError("new_content must be a string")
    
    if "text" not in composition:
        composition["text"] = {}
    
    composition["text"]["div"] = new_content
    return True


def extract_text_content(html_content: str) -> str:
    """
    Extract plain text from HTML content
    
    Removes all HTML tags and returns clean text.
    
    Args:
        html_content: HTML string
    
    Returns:
        Plain text content
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_content)
    # Decode HTML entities
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&apos;', "'")
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def find_elements_by_class(
    html_content: str,
    class_name: str
) -> List[HtmlElement]:
    """
    Find all HTML elements with a specific class
    
    Args:
        html_content: HTML string
        class_name: CSS class name to search for
    
    Returns:
        List of HtmlElement instances
    """
    elements = []
    
    # Pattern to find class attributes
    pattern = rf'<(\w+)[^>]*class=["\']([^"\']*{class_name}[^"\']*)["\']([^>]*)>'
    
    for match in re.finditer(pattern, html_content):
        tag = match.group(1)
        classes_str = match.group(2)
        classes = classes_str.split()
        
        element = HtmlElement(
            tag=tag,
            class_names=classes,
            position=(match.start(), match.end())
        )
        elements.append(element)
    
    return elements


def find_elements_by_tag(
    html_content: str,
    tag_name: str
) -> List[HtmlElement]:
    """
    Find all elements with a specific tag name
    
    Args:
        html_content: HTML string
        tag_name: Tag name (e.g., 'div', 'p', 'h1')
    
    Returns:
        List of HtmlElement instances
    """
    elements = []
    
    # Pattern to find opening tags
    pattern = rf'<{tag_name}\b[^>]*>'
    
    for match in re.finditer(pattern, html_content):
        element = HtmlElement(
            tag=tag_name,
            position=(match.start(), match.end())
        )
        elements.append(element)
    
    return elements


def replace_html_section(
    html_content: str,
    start_marker: str,
    end_marker: str,
    replacement_content: str
) -> str:
    """
    Replace a section of HTML content between markers
    
    Args:
        html_content: Original HTML string
        start_marker: Beginning marker (exact string)
        end_marker: Ending marker (exact string)
        replacement_content: New content to insert
    
    Returns:
        Modified HTML string
    
    Raises:
        ValueError: If markers not found
    """
    start_pos = html_content.find(start_marker)
    end_pos = html_content.find(end_marker)
    
    if start_pos == -1:
        raise ValueError(f"Start marker not found: {start_marker}")
    if end_pos == -1:
        raise ValueError(f"End marker not found: {end_marker}")
    if start_pos > end_pos:
        raise ValueError("Start marker comes after end marker")
    
    # Keep the markers themselves if they are element tags
    if start_marker.startswith('<'):
        start_end = start_pos + len(start_marker)
    else:
        start_end = start_pos
    
    if end_marker.startswith('<'):
        end_start = end_pos
    else:
        end_start = end_pos + len(end_marker)
    
    return html_content[:start_end] + replacement_content + html_content[end_start:]


def extract_html_sections(html_content: str) -> List[HtmlSection]:
    """
    Extract major HTML sections from content
    
    Groups content into logical sections based on structural tags.
    
    Args:
        html_content: HTML string
    
    Returns:
        List of HtmlSection instances
    """
    sections = []
    
    # Find major structural tags
    tags_to_find = ['section', 'article', 'div', 'main']
    
    for tag in tags_to_find:
        pattern = rf'<{tag}\b[^>]*class=["\']([^"\']*)["\']([^>]*)>'
        
        for match in re.finditer(pattern, html_content):
            class_attr = match.group(1)
            start_pos = match.start()
            
            # Find closing tag
            close_pattern = rf'</{tag}>'
            close_match = re.search(close_pattern, html_content[start_pos:])
            if close_match:
                end_pos = start_pos + close_match.end()
                section = HtmlSection(
                    tag_name=tag,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    class_name=class_attr,
                    content=html_content[start_pos:end_pos]
                )
                sections.append(section)
    
    return sections


def wrap_content_with_element(
    content: str,
    tag_name: str,
    class_names: List[str] = None,
    attributes: Dict[str, str] = None
) -> str:
    """
    Wrap content with an HTML element
    
    Args:
        content: Content to wrap
        tag_name: Tag name (e.g., 'div', 'span', 'p')
        class_names: CSS classes to add
        attributes: Other attributes (e.g., {'id': 'my-id'})
    
    Returns:
        Wrapped HTML string
    
    Example:
        wrap_content_with_element(
            "Hello World",
            "div",
            class_names=["highlight"],
            attributes={"id": "greeting"}
        )
        # Returns: <div id="greeting" class="highlight">Hello World</div>
    """
    if not content or not isinstance(content, str):
        raise ValueError("content must be a non-empty string")
    
    if not tag_name or not isinstance(tag_name, str):
        raise ValueError("tag_name must be a non-empty string")
    
    # Build opening tag
    attrs = attributes or {}
    if class_names:
        attrs["class"] = " ".join(class_names)
    
    # Build attribute string
    attr_parts = []
    for key, value in attrs.items():
        attr_parts.append(f'{key}="{value}"')
    
    attr_str = " " + " ".join(attr_parts) if attr_parts else ""
    
    return f"<{tag_name}{attr_str}>{content}</{tag_name}>"


def get_html_structure_summary(html_content: str) -> Dict[str, Any]:
    """
    Get a summary of HTML document structure
    
    Args:
        html_content: HTML string
    
    Returns:
        Dictionary with structure information
    """
    summary = {
        "total_length": len(html_content),
        "tag_counts": {},
        "class_counts": {},
        "has_tables": False,
        "has_forms": False,
        "has_lists": False,
        "text_length": 0
    }
    
    # Count tags
    tag_pattern = r'<(\w+)\b'
    for match in re.finditer(tag_pattern, html_content):
        tag = match.group(1).lower()
        summary["tag_counts"][tag] = summary["tag_counts"].get(tag, 0) + 1
    
    # Check for specific elements
    summary["has_tables"] = bool(re.search(r'<table', html_content))
    summary["has_forms"] = bool(re.search(r'<form', html_content))
    summary["has_lists"] = bool(re.search(r'<[ou]l', html_content))
    
    # Extract text
    text = extract_text_content(html_content)
    summary["text_length"] = len(text)
    
    # Count classes
    class_pattern = r'class=["\']([^"\']+)["\']'
    for match in re.finditer(class_pattern, html_content):
        classes = match.group(1).split()
        for cls in classes:
            summary["class_counts"][cls] = summary["class_counts"].get(cls, 0) + 1
    
    return summary


def validate_html_content(html_content: str) -> Tuple[bool, List[str]]:
    """
    Validate HTML content for common issues
    
    Args:
        html_content: HTML string
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    if not html_content:
        issues.append("Content is empty")
    
    # Check for unclosed tags
    open_tags = re.findall(r'<(\w+)\b[^>]*(?<!/)>', html_content)
    close_tags = re.findall(r'</(\w+)>', html_content)
    
    for tag in open_tags:
        if tag.lower() not in ['br', 'hr', 'img', 'input', 'meta', 'link']:
            if tag not in close_tags:
                issues.append(f"Unclosed tag: {tag}")
    
    # Check for invalid characters
    if '\x00' in html_content:
        issues.append("Content contains null characters")
    
    # Check namespace declaration
    if '<div xmlns=' not in html_content and '<html xmlns=' not in html_content:
        issues.append("Missing XHTML namespace declaration")
    
    return (len(issues) == 0, issues)
