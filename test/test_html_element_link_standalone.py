#!/usr/bin/env python
"""
Standalone test runner for HtmlElementLink extensions

Avoids connexion/flask import issues by running tests directly
"""

import sys
import json
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from preprocessor.models.html_element_link import (
    HtmlElementLink,
    CodeableReference,
    Coding,
)
from preprocessor.models.html_element_link_manager import (
    list_html_element_links,
    get_html_element_link,
    add_html_element_link,
    remove_html_element_link,
    remove_all_html_element_links,
    filter_html_element_links,
    get_element_classes,
    get_concepts_for_element_class,
)


def test_coding():
    """Test Coding model"""
    print("\n" + "=" * 70)
    print("TEST: Coding Model")
    print("=" * 70)

    # Create coding
    coding = Coding(
        system="http://snomed.info/sct", code="77386006", display="Pregnancy"
    )
    assert coding.system == "http://snomed.info/sct"
    assert coding.code == "77386006"
    assert coding.display == "Pregnancy"
    print("✓ Coding creation")

    # Serialize
    data = coding.to_dict()
    assert data["system"] == "http://snomed.info/sct"
    print("✓ Coding serialization")

    # Deserialize
    coding2 = Coding.from_dict(data)
    assert coding == coding2
    print("✓ Coding deserialization")


def test_codeable_reference():
    """Test CodeableReference model"""
    print("\n" + "=" * 70)
    print("TEST: CodeableReference Model")
    print("=" * 70)

    coding = Coding(system="http://snomed.info/sct", code="77386006")
    ref = CodeableReference(codings=[coding])
    assert len(ref.codings) == 1
    print("✓ CodeableReference creation")

    data = ref.to_dict()
    ref2 = CodeableReference.from_dict(data)
    assert ref == ref2
    print("✓ CodeableReference serialization/deserialization")


def test_html_element_link():
    """Test HtmlElementLink model"""
    print("\n" + "=" * 70)
    print("TEST: HtmlElementLink Model")
    print("=" * 70)

    coding = Coding(system="http://snomed.info/sct", code="77386006")
    concept = CodeableReference(codings=[coding])
    link = HtmlElementLink(element_class="pregnancyCategory", concept=concept)
    assert link.element_class == "pregnancyCategory"
    print("✓ HtmlElementLink creation")

    data = link.to_dict()
    assert data["url"] == HtmlElementLink.STRUCTURE_DEFINITION_URL
    print("✓ HtmlElementLink serialization")

    link2 = HtmlElementLink.from_dict(data)
    assert link == link2
    print("✓ HtmlElementLink deserialization")


def test_list_extensions():
    """Test listing extensions"""
    print("\n" + "=" * 70)
    print("TEST: List Extensions")
    print("=" * 70)

    composition = {
        "extension": [
            {
                "extension": [
                    {"url": "elementClass", "valueString": "pregnancyCategory"},
                    {
                        "url": "concept",
                        "valueCodeableReference": {
                            "concept": {
                                "coding": [
                                    {
                                        "system": "http://snomed.info/sct",
                                        "code": "77386006",
                                    }
                                ]
                            }
                        },
                    },
                ],
                "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
            },
            {
                "extension": [
                    {"url": "elementClass", "valueString": "indication"},
                    {
                        "url": "concept",
                        "valueCodeableReference": {
                            "concept": {"coding": [{"code": "B90"}]}
                        },
                    },
                ],
                "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
            },
        ]
    }

    links = list_html_element_links(composition)
    assert len(links) == 2
    assert links[0].element_class == "pregnancyCategory"
    assert links[1].element_class == "indication"
    print(f"✓ List extensions: Found {len(links)} extensions")


def test_get_extension():
    """Test getting a specific extension"""
    print("\n" + "=" * 70)
    print("TEST: Get Specific Extension")
    print("=" * 70)

    composition = {
        "extension": [
            {
                "extension": [
                    {"url": "elementClass", "valueString": "pregnancyCategory"},
                    {"url": "concept", "valueCodeableReference": {"concept": {}}},
                ],
                "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
            }
        ]
    }

    link = get_html_element_link(composition, "pregnancyCategory")
    assert link is not None
    assert link.element_class == "pregnancyCategory"
    print("✓ Get extension found")

    link2 = get_html_element_link(composition, "nonexistent")
    assert link2 is None
    print("✓ Get extension not found")


def test_add_extension():
    """Test adding extensions"""
    print("\n" + "=" * 70)
    print("TEST: Add Extension")
    print("=" * 70)

    composition = {"extension": []}

    coding = Coding(system="http://snomed.info/sct", code="77386006")
    concept = CodeableReference(codings=[coding])
    result = add_html_element_link(composition, "pregnancyCategory", concept)
    assert result is True
    assert len(composition["extension"]) == 1
    print("✓ Add extension to empty composition")

    # Try adding duplicate
    result2 = add_html_element_link(composition, "pregnancyCategory", concept)
    assert result2 is False
    print("✓ Duplicate add rejected")

    # Add with replace
    result3 = add_html_element_link(composition, "pregnancyCategory", concept, replace_if_exists=True)
    assert result3 is True
    print("✓ Duplicate replaced")


def test_remove_extension():
    """Test removing extensions"""
    print("\n" + "=" * 70)
    print("TEST: Remove Extension")
    print("=" * 70)

    composition = {
        "extension": [
            {
                "extension": [
                    {"url": "elementClass", "valueString": "pregnancyCategory"},
                    {"url": "concept", "valueCodeableReference": {}},
                ],
                "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
            },
            {
                "extension": [
                    {"url": "elementClass", "valueString": "indication"},
                    {"url": "concept", "valueCodeableReference": {}},
                ],
                "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
            },
        ]
    }

    result = remove_html_element_link(composition, "pregnancyCategory")
    assert result is True
    assert len(composition["extension"]) == 1
    print("✓ Remove extension")

    result2 = remove_html_element_link(composition, "nonexistent")
    assert result2 is False
    print("✓ Remove nonexistent fails")


def test_remove_all_extensions():
    """Test removing all extensions"""
    print("\n" + "=" * 70)
    print("TEST: Remove All Extensions")
    print("=" * 70)

    composition = {
        "extension": [
            {
                "extension": [
                    {"url": "elementClass", "valueString": "pregnancyCategory"},
                    {"url": "concept", "valueCodeableReference": {}},
                ],
                "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
            },
            {
                "extension": [
                    {"url": "elementClass", "valueString": "indication"},
                    {"url": "concept", "valueCodeableReference": {}},
                ],
                "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
            },
        ]
    }

    count = remove_all_html_element_links(composition)
    assert count == 2
    assert len(composition.get("extension", [])) == 0
    print(f"✓ Remove all extensions: Removed {count} extensions")


def test_filter_extensions():
    """Test filtering extensions"""
    print("\n" + "=" * 70)
    print("TEST: Filter Extensions")
    print("=" * 70)

    composition = {
        "extension": [
            {
                "extension": [
                    {"url": "elementClass", "valueString": "pregnancyCategory"},
                    {"url": "concept", "valueCodeableReference": {"concept": {}}},
                ],
                "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
            },
            {
                "extension": [
                    {"url": "elementClass", "valueString": "indication"},
                    {"url": "concept", "valueCodeableReference": {"concept": {}}},
                ],
                "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
            },
        ]
    }

    # Filter all
    links = filter_html_element_links(composition)
    assert len(links) == 2
    print("✓ Filter all (no predicate)")

    # Filter by pattern
    links = filter_html_element_links(
        composition, lambda l: "pregnancy" in l.element_class.lower()
    )
    assert len(links) == 1
    print("✓ Filter by element class pattern")


def test_get_element_classes():
    """Test getting element classes"""
    print("\n" + "=" * 70)
    print("TEST: Get Element Classes")
    print("=" * 70)

    composition = {
        "extension": [
            {
                "extension": [
                    {"url": "elementClass", "valueString": "pregnancyCategory"},
                    {"url": "concept", "valueCodeableReference": {}},
                ],
                "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
            },
            {
                "extension": [
                    {"url": "elementClass", "valueString": "indication"},
                    {"url": "concept", "valueCodeableReference": {}},
                ],
                "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
            },
        ]
    }

    classes = get_element_classes(composition)
    assert len(classes) == 2
    assert "pregnancyCategory" in classes
    assert "indication" in classes
    print(f"✓ Get element classes: {classes}")


def test_real_epis():
    """Test with real ePIs from test data"""
    print("\n" + "=" * 70)
    print("TEST: Real ePIs from Test Data")
    print("=" * 70)

    test_folder = Path(__file__).parent / "testing ePIs"
    if not test_folder.exists():
        test_folder = project_root / "test" / "testing ePIs"

    if not test_folder.exists():
        print("⚠ Test folder not found, skipping real ePIs tests")
        return

    epi_files = list(test_folder.glob("*.json"))
    print(f"\n Found {len(epi_files)} real ePIs")

    test_count = 0
    total_links = 0

    for file_path in epi_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                bundle = json.load(f)

            # Find composition
            entries = bundle.get("entry", [])
            for entry in entries:
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Composition":
                    links = list_html_element_links(resource)
                    if links:
                        test_count += 1
                        total_links += len(links)
                        print(
                            f"\n  {file_path.name}:"
                        )
                        print(
                            f"    - Found {len(links)} HtmlElementLink extensions"
                        )

                        classes = get_element_classes(resource)
                        print(f"    - Element classes: {', '.join(classes[:5])}")
                        if len(classes) > 5:
                            print(f"      ... and {len(classes) - 5} more")

                        # Test add/remove
                        original_count = len(links)
                        coding = Coding(system="test", code="test")
                        concept = CodeableReference(codings=[coding])
                        add_html_element_link(
                            resource, "test-element", concept
                        )
                        new_count = len(list_html_element_links(resource))
                        assert new_count == original_count + 1
                        remove_html_element_link(resource, "test-element")
                        final_count = len(list_html_element_links(resource))
                        assert final_count == original_count
                        print(
                            f"    - Add/Remove test: ✓ ({original_count} → {new_count} → {final_count})"
                        )

        except Exception as e:
            print(f"  ⚠ Error processing {file_path.name}: {e}")

    print(f"\n  Total: Tested {test_count} compositions with {total_links} total extensions")
    assert test_count > 0, "No compositions with HtmlElementLink extensions found"
    print("✓ Real ePIs tests passed")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("HtmlElementLink Extension Manager - Test Suite")
    print("=" * 70)

    tests = [
        test_coding,
        test_codeable_reference,
        test_html_element_link,
        test_list_extensions,
        test_get_extension,
        test_add_extension,
        test_remove_extension,
        test_remove_all_extensions,
        test_filter_extensions,
        test_get_element_classes,
        test_real_epis,
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
    sys.exit(main())
