"""
Tests for HtmlElementLink extension management

Tests cover:
  - Creating and serializing HtmlElementLink objects
  - Listing extensions from Composition resources
  - Adding extensions with various scenarios
  - Removing extensions
  - Filtering and querying extensions
  - Real ePIs from test data
"""

import json
import unittest
from pathlib import Path
from typing import Dict, Any

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


class TestCoding(unittest.TestCase):
    """Test Coding model"""

    def test_coding_creation(self):
        """Test creating Coding objects"""
        coding = Coding(
            system="http://snomed.info/sct",
            code="77386006",
            display="Pregnancy",
        )
        self.assertEqual(coding.system, "http://snomed.info/sct")
        self.assertEqual(coding.code, "77386006")
        self.assertEqual(coding.display, "Pregnancy")

    def test_coding_to_dict(self):
        """Test Coding serialization"""
        coding = Coding(
            system="http://snomed.info/sct",
            code="77386006",
            display="Pregnancy",
        )
        data = coding.to_dict()
        self.assertEqual(data["system"], "http://snomed.info/sct")
        self.assertEqual(data["code"], "77386006")
        self.assertEqual(data["display"], "Pregnancy")

    def test_coding_from_dict(self):
        """Test Coding deserialization"""
        data = {
            "system": "http://snomed.info/sct",
            "code": "77386006",
            "display": "Pregnancy",
        }
        coding = Coding.from_dict(data)
        self.assertEqual(coding.system, "http://snomed.info/sct")
        self.assertEqual(coding.code, "77386006")
        self.assertEqual(coding.display, "Pregnancy")

    def test_coding_equality(self):
        """Test Coding equality"""
        coding1 = Coding(system="http://snomed.info/sct", code="77386006")
        coding2 = Coding(system="http://snomed.info/sct", code="77386006")
        coding3 = Coding(system="http://snomed.info/sct", code="69840006")
        self.assertEqual(coding1, coding2)
        self.assertNotEqual(coding1, coding3)


class TestCodeableReference(unittest.TestCase):
    """Test CodeableReference model"""

    def test_codeable_reference_creation(self):
        """Test creating CodeableReference objects"""
        coding = Coding(system="http://snomed.info/sct", code="77386006")
        ref = CodeableReference(codings=[coding])
        self.assertEqual(len(ref.codings), 1)
        self.assertEqual(ref.codings[0], coding)

    def test_codeable_reference_empty(self):
        """Test empty CodeableReference"""
        ref = CodeableReference()
        self.assertEqual(len(ref.codings), 0)

    def test_codeable_reference_from_dict(self):
        """Test CodeableReference deserialization"""
        data = {
            "concept": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "77386006",
                        "display": "Pregnancy",
                    }
                ]
            }
        }
        ref = CodeableReference.from_dict(data)
        self.assertEqual(len(ref.codings), 1)
        self.assertEqual(ref.codings[0].code, "77386006")

    def test_codeable_reference_to_dict(self):
        """Test CodeableReference serialization"""
        coding = Coding(
            system="http://snomed.info/sct",
            code="77386006",
            display="Pregnancy",
        )
        ref = CodeableReference(codings=[coding])
        data = ref.to_dict()
        self.assertIn("concept", data)
        self.assertIn("coding", data["concept"])
        self.assertEqual(data["concept"]["coding"][0]["code"], "77386006")


class TestHtmlElementLink(unittest.TestCase):
    """Test HtmlElementLink model"""

    def test_html_element_link_creation(self):
        """Test creating HtmlElementLink objects"""
        coding = Coding(system="http://snomed.info/sct", code="77386006")
        concept = CodeableReference(codings=[coding])
        link = HtmlElementLink(element_class="pregnancyCategory", concept=concept)
        self.assertEqual(link.element_class, "pregnancyCategory")
        self.assertEqual(link.concept, concept)

    def test_html_element_link_from_dict(self):
        """Test HtmlElementLink deserialization"""
        data = {
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
                                    "display": "Pregnancy",
                                }
                            ]
                        }
                    },
                },
            ],
            "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
        }
        link = HtmlElementLink.from_dict(data)
        self.assertEqual(link.element_class, "pregnancyCategory")
        self.assertEqual(len(link.concept.codings), 1)

    def test_html_element_link_to_dict(self):
        """Test HtmlElementLink serialization"""
        coding = Coding(system="http://snomed.info/sct", code="77386006")
        concept = CodeableReference(codings=[coding])
        link = HtmlElementLink(element_class="pregnancyCategory", concept=concept)
        data = link.to_dict()
        self.assertEqual(data["url"], HtmlElementLink.STRUCTURE_DEFINITION_URL)
        self.assertEqual(len(data["extension"]), 2)

    def test_html_element_link_string_representation(self):
        """Test HtmlElementLink string representation"""
        coding = Coding(
            system="http://snomed.info/sct",
            code="77386006",
            display="Pregnancy",
        )
        concept = CodeableReference(codings=[coding])
        link = HtmlElementLink(element_class="pregnancyCategory", concept=concept)
        str_repr = str(link)
        self.assertIn("pregnancyCategory", str_repr)
        self.assertIn("Pregnancy", str_repr)


class TestHtmlElementLinkManager(unittest.TestCase):
    """Test HtmlElementLink extension manager functions"""

    def setUp(self):
        """Create a sample Composition resource for testing"""
        self.composition = {
            "resourceType": "Composition",
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
                                            "display": "Pregnancy",
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
                                "concept": {
                                    "coding": [
                                        {
                                            "system": "https://icpc2.icd.com/",
                                            "code": "B90",
                                            "display": "HIV-infection/AIDS",
                                        }
                                    ]
                                }
                            },
                        },
                    ],
                    "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink",
                },
            ],
        }

    def test_list_html_element_links(self):
        """Test listing HtmlElementLink extensions"""
        links = list_html_element_links(self.composition)
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0].element_class, "pregnancyCategory")
        self.assertEqual(links[1].element_class, "indication")

    def test_list_empty_composition(self):
        """Test listing from composition with no extensions"""
        comp = {"resourceType": "Composition"}
        links = list_html_element_links(comp)
        self.assertEqual(len(links), 0)

    def test_get_html_element_link(self):
        """Test getting a specific extension by element class"""
        link = get_html_element_link(self.composition, "pregnancyCategory")
        self.assertIsNotNone(link)
        self.assertEqual(link.element_class, "pregnancyCategory")

    def test_get_html_element_link_not_found(self):
        """Test getting non-existent extension"""
        link = get_html_element_link(self.composition, "nonexistent")
        self.assertIsNone(link)

    def test_add_html_element_link(self):
        """Test adding a new extension"""
        coding = Coding(system="http://snomed.info/sct", code="69840006")
        concept = CodeableReference(codings=[coding])

        result = add_html_element_link(
            self.composition, "breastfeedingCategory", concept
        )

        self.assertTrue(result)
        self.assertEqual(len(self.composition["extension"]), 3)

        link = get_html_element_link(self.composition, "breastfeedingCategory")
        self.assertIsNotNone(link)
        self.assertEqual(link.element_class, "breastfeedingCategory")

    def test_add_duplicate_extension_no_replace(self):
        """Test adding duplicate extension without replacement"""
        coding = Coding(system="http://snomed.info/sct", code="99999999")
        concept = CodeableReference(codings=[coding])

        result = add_html_element_link(
            self.composition, "pregnancyCategory", concept, replace_if_exists=False
        )

        self.assertFalse(result)
        self.assertEqual(len(self.composition["extension"]), 2)

    def test_add_duplicate_extension_with_replace(self):
        """Test adding duplicate extension with replacement"""
        coding = Coding(system="http://snomed.info/sct", code="99999999")
        concept = CodeableReference(codings=[coding])

        result = add_html_element_link(
            self.composition, "pregnancyCategory", concept, replace_if_exists=True
        )

        self.assertTrue(result)
        self.assertEqual(len(self.composition["extension"]), 2)

        link = get_html_element_link(self.composition, "pregnancyCategory")
        self.assertEqual(link.concept.codings[0].code, "99999999")

    def test_add_invalid_element_class(self):
        """Test adding with invalid element_class"""
        coding = Coding(system="http://snomed.info/sct", code="12345")
        concept = CodeableReference(codings=[coding])

        with self.assertRaises(ValueError):
            add_html_element_link(self.composition, "", concept)

        with self.assertRaises(ValueError):
            add_html_element_link(self.composition, None, concept)

    def test_add_invalid_concept(self):
        """Test adding with invalid concept"""
        with self.assertRaises(ValueError):
            add_html_element_link(self.composition, "test", "not_a_concept")

    def test_remove_html_element_link(self):
        """Test removing an extension"""
        result = remove_html_element_link(self.composition, "pregnancyCategory")
        self.assertTrue(result)
        self.assertEqual(len(self.composition["extension"]), 1)
        self.assertIsNone(get_html_element_link(self.composition, "pregnancyCategory"))

    def test_remove_nonexistent_extension(self):
        """Test removing non-existent extension"""
        result = remove_html_element_link(self.composition, "nonexistent")
        self.assertFalse(result)
        self.assertEqual(len(self.composition["extension"]), 2)

    def test_remove_from_empty_composition(self):
        """Test removing from composition with no extensions"""
        comp = {"resourceType": "Composition"}
        result = remove_html_element_link(comp, "something")
        self.assertFalse(result)

    def test_remove_all_html_element_links(self):
        """Test removing all extensions"""
        count = remove_all_html_element_links(self.composition)
        self.assertEqual(count, 2)
        self.assertEqual(len(self.composition.get("extension", [])), 0)

    def test_filter_html_element_links_all(self):
        """Test filtering without predicate (return all)"""
        links = filter_html_element_links(self.composition)
        self.assertEqual(len(links), 2)

    def test_filter_html_element_links_by_element_class(self):
        """Test filtering by element class pattern"""
        links = filter_html_element_links(
            self.composition, lambda l: "pregnancy" in l.element_class.lower()
        )
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].element_class, "pregnancyCategory")

    def test_filter_html_element_links_by_concept_system(self):
        """Test filtering by concept system"""
        links = filter_html_element_links(
            self.composition,
            lambda l: (
                l.concept.codings[0].system == "http://snomed.info/sct"
                if l.concept.codings
                else False
            ),
        )
        self.assertEqual(len(links), 1)

    def test_get_element_classes(self):
        """Test getting all element classes"""
        classes = get_element_classes(self.composition)
        self.assertEqual(len(classes), 2)
        self.assertIn("pregnancyCategory", classes)
        self.assertIn("indication", classes)

    def test_get_concepts_for_element_class(self):
        """Test getting concepts for an element class"""
        concepts = get_concepts_for_element_class(self.composition, "pregnancyCategory")
        self.assertEqual(len(concepts), 1)
        self.assertEqual(concepts[0].code, "77386006")

    def test_get_concepts_for_nonexistent_element_class(self):
        """Test getting concepts for non-existent element class"""
        concepts = get_concepts_for_element_class(self.composition, "nonexistent")
        self.assertEqual(len(concepts), 0)


class TestRealEPIs(unittest.TestCase):
    """Test with real ePI data from test files"""

    @classmethod
    def setUpClass(cls):
        """Load real ePIs from test folder"""
        test_folder = Path(__file__).parent / "testing ePIs"
        if not test_folder.exists():
            # Try alternative path
            test_folder = (
                Path(__file__).parent.parent / "test" / "testing ePIs"
            )

        cls.epi_files = list(test_folder.glob("*.json"))
        cls.test_data = {}

        for file_path in cls.epi_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    cls.test_data[file_path.stem] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load {file_path}: {e}")

    def test_real_epis_loaded(self):
        """Verify real ePIs are loaded"""
        self.assertGreater(len(self.test_data), 0, "No real ePIs found")

    def test_real_epis_have_html_element_links(self):
        """Test that real ePIs contain HtmlElementLink extensions"""
        found_links = False
        for epi_name, bundle in self.test_data.items():
            # Find composition in bundle
            entries = bundle.get("entry", [])
            for entry in entries:
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Composition":
                    links = list_html_element_links(resource)
                    if links:
                        found_links = True
                        print(f"\n{epi_name}: Found {len(links)} HtmlElementLink extensions")

        self.assertTrue(found_links, "No HtmlElementLink extensions found in real ePIs")

    def test_real_epis_list_extensions(self):
        """Test listing extensions from real ePIs"""
        for epi_name, bundle in self.test_data.items():
            entries = bundle.get("entry", [])
            for entry in entries:
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Composition":
                    links = list_html_element_links(resource)
                    if links:
                        print(f"\n{epi_name} - Extensions:")
                        for link in links:
                            print(f"  - {link}")

    def test_real_epis_get_element_classes(self):
        """Test getting element classes from real ePIs"""
        for epi_name, bundle in self.test_data.items():
            entries = bundle.get("entry", [])
            for entry in entries:
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Composition":
                    classes = get_element_classes(resource)
                    if classes:
                        print(f"\n{epi_name} - Element classes: {classes}")

    def test_real_epis_add_remove_extensions(self):
        """Test adding and removing extensions in real ePIs"""
        for epi_name, bundle in self.test_data.items():
            entries = bundle.get("entry", [])
            for entry in entries:
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Composition":
                    original_count = len(list_html_element_links(resource))
                    if original_count > 0:
                        # Add a new extension
                        coding = Coding(system="test-system", code="test-code")
                        concept = CodeableReference(codings=[coding])
                        add_html_element_link(resource, "test-element", concept)

                        # Verify it was added
                        new_count = len(list_html_element_links(resource))
                        self.assertEqual(new_count, original_count + 1)

                        # Remove it
                        remove_html_element_link(resource, "test-element")
                        final_count = len(list_html_element_links(resource))
                        self.assertEqual(final_count, original_count)

                        print(
                            f"\n{epi_name}: Add/Remove test passed ({original_count} → {new_count} → {final_count})"
                        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
