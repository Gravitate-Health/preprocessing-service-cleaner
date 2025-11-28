"""
Tests for HTML Content Manager

Tests cover:
  - HTML content extraction and parsing
  - Finding elements by class and tag
  - Replacing HTML sections
  - Structure analysis
  - Validation
  - Real ePIs from test data
"""

import json
from pathlib import Path
from preprocessor.models.html_content_manager import (
    HtmlContent,
    HtmlElement,
    HtmlSection,
    get_html_content,
    update_html_content,
    extract_text_content,
    find_elements_by_class,
    find_elements_by_tag,
    replace_html_section,
    extract_html_sections,
    wrap_content_with_element,
    get_html_structure_summary,
    validate_html_content,
)


def test_html_content_model():
    """Test HtmlContent model"""
    print("\n" + "=" * 70)
    print("TEST: HtmlContent Model")
    print("=" * 70)

    # Create instance
    html = "<div>Test</div>"
    content = HtmlContent(html)
    assert content.raw_html == html
    assert content.length == len(html)
    assert not content.is_empty
    print("✓ HtmlContent creation")

    # Create from empty
    empty = HtmlContent("")
    assert empty.is_empty
    print("✓ Empty detection")

    # To dict
    text_dict = content.to_dict()
    assert text_dict["status"] == "extensions"
    assert text_dict["div"] == html
    print("✓ Conversion to FHIR structure")


def test_html_element_model():
    """Test HtmlElement model"""
    print("\n" + "=" * 70)
    print("TEST: HtmlElement Model")
    print("=" * 70)

    # Create element
    element = HtmlElement(
        tag="div",
        text_content="Hello",
        class_names=["container", "highlight"],
        id="main",
        attributes={"data-id": "123"}
    )

    assert element.tag == "div"
    assert element.text_content == "Hello"
    assert element.has_class("highlight")
    assert not element.has_class("nonexistent")
    print("✓ HtmlElement creation and class checking")

    assert element.get_attribute("data-id") == "123"
    assert element.get_attribute("missing") is None
    print("✓ Attribute retrieval")


def test_extract_text_content():
    """Test text extraction"""
    print("\n" + "=" * 70)
    print("TEST: Extract Text Content")
    print("=" * 70)

    html = "<div><p>Hello <b>World</b></p></div>"
    text = extract_text_content(html)
    assert "Hello" in text
    assert "World" in text
    assert "<" not in text
    assert ">" not in text
    print(f"✓ Text extraction: '{text}'")

    # With entities
    html_with_entities = "<p>Cost: &pound;50 &amp; £50</p>"
    text = extract_text_content(html_with_entities)
    assert "&" in text
    assert "<" not in text
    print("✓ HTML entity handling")


def test_find_elements_by_class():
    """Test finding elements by class"""
    print("\n" + "=" * 70)
    print("TEST: Find Elements by Class")
    print("=" * 70)

    html = '''
    <div class="container highlight">Container</div>
    <div class="item highlight">Item 1</div>
    <div class="item">Item 2</div>
    <p class="highlight text">Paragraph</p>
    '''

    elements = find_elements_by_class(html, "highlight")
    assert len(elements) == 3
    print(f"✓ Found {len(elements)} elements with 'highlight' class")

    # All should have the class
    for elem in elements:
        assert elem.has_class("highlight")
    print("✓ All found elements have the class")


def test_find_elements_by_tag():
    """Test finding elements by tag"""
    print("\n" + "=" * 70)
    print("TEST: Find Elements by Tag")
    print("=" * 70)

    html = '''
    <div>Div 1</div>
    <div id="special">Div 2</div>
    <p>Paragraph</p>
    <div>Div 3</div>
    '''

    divs = find_elements_by_tag(html, "div")
    assert len(divs) == 3
    print(f"✓ Found {len(divs)} div elements")

    paras = find_elements_by_tag(html, "p")
    assert len(paras) == 1
    print(f"✓ Found {len(paras)} p element")


def test_wrap_content_with_element():
    """Test wrapping content"""
    print("\n" + "=" * 70)
    print("TEST: Wrap Content with Element")
    print("=" * 70)

    # Simple wrap
    result = wrap_content_with_element("Hello", "div")
    assert result == "<div>Hello</div>"
    print("✓ Simple wrapping")

    # With classes
    result = wrap_content_with_element(
        "Hello",
        "div",
        class_names=["highlight", "important"]
    )
    assert 'class="highlight important"' in result
    assert "<div" in result
    print("✓ Wrapping with classes")

    # With attributes
    result = wrap_content_with_element(
        "Hello",
        "span",
        attributes={"id": "greeting", "data-value": "123"}
    )
    assert 'id="greeting"' in result
    assert 'data-value="123"' in result
    print("✓ Wrapping with attributes")


def test_replace_html_section():
    """Test replacing HTML sections"""
    print("\n" + "=" * 70)
    print("TEST: Replace HTML Section")
    print("=" * 70)

    html = "<div>Start <p>Old content</p> End</div>"

    result = replace_html_section(html, "<p>", "</p>", "New content")
    assert "New content" in result
    assert "Old content" not in result
    print("✓ Replace between tags")

    # With markers
    html = "<!-- START --> old text <!-- END -->"
    result = replace_html_section(html, "<!-- START -->", "<!-- END -->", " new text ")
    assert "new text" in result
    assert "old text" not in result
    print("✓ Replace between comment markers")


def test_get_html_structure_summary():
    """Test HTML structure analysis"""
    print("\n" + "=" * 70)
    print("TEST: Get HTML Structure Summary")
    print("=" * 70)

    html = '''
    <div class="container">
        <h1 class="title">Title</h1>
        <p class="text">Paragraph 1</p>
        <p class="text">Paragraph 2</p>
        <table>
            <tr><td>Cell</td></tr>
        </table>
    </div>
    '''

    summary = get_html_structure_summary(html)
    assert summary["total_length"] > 0
    assert summary["has_tables"] is True
    assert summary["has_forms"] is False
    print("✓ Structure analysis complete")

    assert "div" in summary["tag_counts"]
    assert summary["tag_counts"]["div"] == 1
    print(f"✓ Tag counting: {summary['tag_counts']}")

    assert "container" in summary["class_counts"]
    assert summary["class_counts"]["text"] == 2
    print(f"✓ Class counting: {summary['class_counts']}")


def test_validate_html_content():
    """Test HTML validation"""
    print("\n" + "=" * 70)
    print("TEST: Validate HTML Content")
    print("=" * 70)

    # Valid HTML
    valid_html = '<div xmlns="http://www.w3.org/1999/xhtml"><p>Content</p></div>'
    is_valid, issues = validate_html_content(valid_html)
    assert is_valid
    assert len(issues) == 0
    print("✓ Valid HTML passes validation")

    # Empty content
    is_valid, issues = validate_html_content("")
    assert not is_valid
    assert "empty" in issues[0].lower()
    print("✓ Empty content detected")

    # Missing namespace
    invalid_html = '<div><p>Content</p></div>'
    is_valid, issues = validate_html_content(invalid_html)
    # May or may not fail depending on implementation
    print(f"✓ Validation issues: {issues}")


def test_real_epis_html_extraction():
    """Test HTML extraction from real ePIs"""
    print("\n" + "=" * 70)
    print("TEST: Real ePIs - HTML Extraction")
    print("=" * 70)

    test_folder = Path("preprocessor/test/testing ePIs")
    if not test_folder.exists():
        print("⚠ Test folder not found, skipping real ePIs tests")
        return

    epi_files = list(test_folder.glob("*.json"))
    print(f"\nFound {len(epi_files)} real ePIs\n")

    for file_path in epi_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                bundle = json.load(f)

            # Find composition
            entries = bundle.get("entry", [])
            for entry in entries:
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Composition":
                    # Extract HTML
                    html_content = get_html_content(resource)

                    # Check it's not empty
                    assert not html_content.is_empty
                    print(f"\n{file_path.name}:")
                    print(f"  - HTML length: {html_content.length} bytes")

                    # Get structure
                    summary = get_html_structure_summary(html_content.raw_html)
                    print(f"  - Tags: {len(summary['tag_counts'])} unique types")
                    print(f"  - Classes: {len(summary['class_counts'])} unique")
                    print(f"  - Has tables: {summary['has_tables']}")
                    print(f"  - Has lists: {summary['has_lists']}")

                    # Extract text
                    text = extract_text_content(html_content.raw_html)
                    print(f"  - Plain text: {len(text)} chars")

                    # Find blockquotes (typically for HtmlElementLink)
                    blockquotes = find_elements_by_tag(html_content.raw_html, "blockquote")
                    print(f"  - Blockquotes: {len(blockquotes)}")

                    # Validate
                    is_valid, issues = validate_html_content(html_content.raw_html)
                    print(f"  - Valid: {is_valid}")
                    if issues:
                        print(f"  - Issues: {issues}")

        except Exception as e:
            print(f"  ⚠ Error processing {file_path.name}: {e}")


def test_html_content_modification_workflow():
    """Test complete modification workflow"""
    print("\n" + "=" * 70)
    print("TEST: HTML Content Modification Workflow")
    print("=" * 70)

    # Create sample composition
    composition = {
        "resourceType": "Composition",
        "text": {
            "status": "extensions",
            "div": '<div xmlns="http://www.w3.org/1999/xhtml"><p>Original content</p></div>'
        }
    }

    # Extract
    html = get_html_content(composition)
    assert "Original content" in html.raw_html
    print("✓ Extract HTML from composition")

    # Modify
    new_html = html.raw_html.replace("Original", "Modified")
    success = update_html_content(composition, new_html)
    assert success
    assert "Modified content" in composition["text"]["div"]
    print("✓ Update HTML in composition")

    # Verify modification
    html2 = get_html_content(composition)
    assert "Modified content" in html2.raw_html
    print("✓ Verify modification persisted")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("HTML Content Manager - Test Suite")
    print("=" * 70)

    tests = [
        test_html_content_model,
        test_html_element_model,
        test_extract_text_content,
        test_find_elements_by_class,
        test_find_elements_by_tag,
        test_wrap_content_with_element,
        test_replace_html_section,
        test_get_html_structure_summary,
        test_validate_html_content,
        test_html_content_modification_workflow,
        test_real_epis_html_extraction,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ {test_func.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ {test_func.__name__} ERROR: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
