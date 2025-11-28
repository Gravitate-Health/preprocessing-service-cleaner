"""
Standalone test runner for HTML optimization and cleanup logic.

Tests HTML optimization, class extraction, and HtmlElementLink cleanup.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from preprocessor.models.html_optimizer import (
    optimize_html,
    extract_html_classes,
    validate_content_integrity
)
from preprocessor.models.html_element_link_cleanup import (
    cleanup_unused_html_element_links,
    analyze_html_element_link_usage
)
from preprocessor.models.html_element_link_manager import (
    add_html_element_link,
    list_html_element_links
)
from preprocessor.models.html_element_link import CodeableReference, Coding


def test_remove_empty_span():
    """Test removing empty span tags without attributes"""
    html = '<div><span></span><p>Content</p></div>'
    result = optimize_html(html)
    assert '<span></span>' not in result
    assert '<p>Content</p>' in result
    print("✓ test_remove_empty_span passed")


def test_remove_empty_div_with_whitespace():
    """Test removing div with only whitespace"""
    html = '<div><div>  </div><p>Content</p></div>'
    result = optimize_html(html)
    assert result.count('<div>') <= 1  # Should remove inner empty div
    assert '<p>Content</p>' in result
    print("✓ test_remove_empty_div_with_whitespace passed")


def test_keep_span_with_class():
    """Test keeping span with class attribute"""
    html = '<div><span class="important"></span><p>Content</p></div>'
    result = optimize_html(html)
    assert 'class="important"' in result
    print("✓ test_keep_span_with_class passed")


def test_simplify_nested_p_tags():
    """Test simplifying nested p tags with classes"""
    html = '<div><p class="c1"><p class="c2">hello</p></p></div>'
    result = optimize_html(html)
    # Should merge into single p tag with both classes
    assert result.count('<p') == 1
    assert 'c1' in result
    assert 'c2' in result
    assert 'hello' in result
    print("✓ test_simplify_nested_p_tags passed")


def test_simplify_nested_divs():
    """Test simplifying nested div tags"""
    html = '<div class="outer"><div class="inner">Content here</div></div>'
    result = optimize_html(html)
    # Should have one div with both classes
    assert result.count('<div') == 1
    assert 'outer' in result
    assert 'inner' in result
    assert 'Content here' in result
    print("✓ test_simplify_nested_divs passed")


def test_preserve_different_nested_tags():
    """Test that different nested tags are NOT simplified"""
    html = '<div><p>Paragraph in div</p></div>'
    result = optimize_html(html)
    # Should keep both div and p
    assert '<div>' in result or '<div ' in result
    assert '<p>' in result or '<p ' in result
    print("✓ test_preserve_different_nested_tags passed")


def test_extract_classes():
    """Test extracting CSS classes from HTML"""
    html = '''
    <div class="container">
        <p class="text important">Hello</p>
        <span class="highlight">World</span>
    </div>
    '''
    classes = extract_html_classes(html)
    assert 'container' in classes
    assert 'text' in classes
    assert 'important' in classes
    assert 'highlight' in classes
    assert len(classes) == 4
    print("✓ test_extract_classes passed")


def test_extract_classes_empty_html():
    """Test extracting classes from empty HTML"""
    classes = extract_html_classes('')
    assert len(classes) == 0
    print("✓ test_extract_classes_empty_html passed")


def test_validate_content_integrity():
    """Test content integrity validation"""
    original = '<div><span></span><p>Important content</p></div>'
    optimized = '<div><p>Important content</p></div>'
    assert validate_content_integrity(original, optimized)
    
    # Test with different content
    wrong = '<div><p>Different content</p></div>'
    assert not validate_content_integrity(original, wrong)
    print("✓ test_validate_content_integrity passed")


def test_cleanup_unused_links():
    """Test removing unused HtmlElementLink extensions"""
    composition = {
        'resourceType': 'Composition',
        'text': {
            'div': '<div><p class="used-class">Content</p></div>'
        },
        'extension': []
    }
    
    # Add two links, one used and one unused
    used_concept = CodeableReference([Coding(code='used', display='Used')])
    unused_concept = CodeableReference([Coding(code='unused', display='Unused')])
    add_html_element_link(composition, 'used-class', used_concept)
    add_html_element_link(composition, 'unused-class', unused_concept)
    
    assert len(list_html_element_links(composition)) == 2
    
    # Extract classes from HTML
    html_classes = extract_html_classes(composition['text']['div'])
    
    # Cleanup unused
    stats = cleanup_unused_html_element_links(composition, html_classes)
    
    assert stats['total'] == 2
    assert stats['removed'] == 1
    assert stats['kept'] == 1
    
    # Verify only used-class remains
    remaining = list_html_element_links(composition)
    assert len(remaining) == 1
    assert remaining[0].element_class == 'used-class'
    
    print("✓ test_cleanup_unused_links passed")


def test_analyze_usage():
    """Test analyzing HtmlElementLink usage"""
    composition = {
        'resourceType': 'Composition',
        'text': {
            'div': '<div><p class="in-html">Content</p></div>'
        },
        'extension': []
    }
    
    add_html_element_link(composition, 'in-html', CodeableReference([Coding(code='test', display='Test')]))
    add_html_element_link(composition, 'not-in-html', CodeableReference([Coding(code='unused', display='Unused')]))
    
    analysis = analyze_html_element_link_usage(composition, composition['text']['div'])
    
    assert 'in-html' in analysis['html_classes']
    assert 'in-html' in analysis['extension_classes']
    assert 'not-in-html' in analysis['extension_classes']
    assert 'in-html' in analysis['used_classes']
    assert 'not-in-html' in analysis['unused_extension_classes']
    
    print("✓ test_analyze_usage passed")


def test_complex_optimization():
    """Test complex real-world scenario"""
    html = '''
    <div xmlns="http://www.w3.org/1999/xhtml">
        <div>
            <span></span>
            <p class="heading"><p class="title">Product Information</p></p>
        </div>
        <div>
            <div class="section">
                <span class="label">Name:</span>
                <span>   </span>
                <span class="value">Example Drug</span>
            </div>
        </div>
    </div>
    '''
    
    result = optimize_html(html)
    
    # Should remove empty spans
    assert result.count('<span></span>') == 0
    assert result.count('<span>   </span>') == 0
    
    # Should simplify nested p tags
    simplified_p_count = result.count('<p')
    assert simplified_p_count == 1  # Two nested p tags should become one
    
    # Should keep spans with classes
    assert 'class="label"' in result
    assert 'class="value"' in result
    
    # Content should be preserved
    assert 'Product Information' in result
    assert 'Example Drug' in result
    
    # Validate integrity
    assert validate_content_integrity(html, result)
    
    print("✓ test_complex_optimization passed")


def test_real_epi_files():
    """Test with real ePI bundle files"""
    test_dir = Path(__file__).parent / 'testing ePIs'
    
    if not test_dir.exists():
        print("⊘ Skipping real ePI tests (test directory not found)")
        return
    
    json_files = list(test_dir.glob('*.json'))
    
    if not json_files:
        print("⊘ Skipping real ePI tests (no JSON files found)")
        return
    
    print(f"\nTesting with {len(json_files)} real ePI files...")
    
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            bundle = json.load(f)
        
        compositions = [
            entry['resource'] 
            for entry in bundle.get('entry', [])
            if entry.get('resource', {}).get('resourceType') == 'Composition'
        ]
        
        for comp in compositions:
            if 'text' in comp and 'div' in comp['text']:
                original_html = comp['text']['div']
                
                # Optimize
                optimized = optimize_html(original_html)
                
                # Validate
                assert validate_content_integrity(original_html, optimized), \
                    f"Content integrity failed for {json_file.name}"
                
                # Extract classes
                classes = extract_html_classes(optimized)
                
                # Test cleanup if extensions exist
                if 'extension' in comp:
                    original_ext_count = len(comp.get('extension', []))
                    cleanup_stats = cleanup_unused_html_element_links(comp, classes)
                    
                    print(f"  {json_file.name}: "
                          f"{len(original_html)} -> {len(optimized)} chars, "
                          f"{len(classes)} classes, "
                          f"{cleanup_stats['removed']} links removed")
    
    print("✓ test_real_epi_files passed")


def run_all_tests():
    """Run all test groups"""
    print("=" * 60)
    print("HTML Optimization and Cleanup Tests")
    print("=" * 60)
    
    test_groups = [
        ("Empty Tag Removal", [
            test_remove_empty_span,
            test_remove_empty_div_with_whitespace,
            test_keep_span_with_class
        ]),
        ("Nested Tag Simplification", [
            test_simplify_nested_p_tags,
            test_simplify_nested_divs,
            test_preserve_different_nested_tags
        ]),
        ("Class Extraction", [
            test_extract_classes,
            test_extract_classes_empty_html
        ]),
        ("Content Validation", [
            test_validate_content_integrity
        ]),
        ("HtmlElementLink Cleanup", [
            test_cleanup_unused_links,
            test_analyze_usage
        ]),
        ("Complex Scenarios", [
            test_complex_optimization
        ]),
        ("Real ePI Files", [
            test_real_epi_files
        ])
    ]
    
    total_passed = 0
    total_failed = 0
    
    for group_name, tests in test_groups:
        print(f"\n{group_name}:")
        print("-" * 60)
        
        for test_func in tests:
            try:
                test_func()
                total_passed += 1
            except AssertionError as e:
                print(f"✗ {test_func.__name__} failed: {e}")
                total_failed += 1
            except Exception as e:
                print(f"✗ {test_func.__name__} error: {e}")
                total_failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {total_passed} passed, {total_failed} failed")
    print("=" * 60)
    
    return total_failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
