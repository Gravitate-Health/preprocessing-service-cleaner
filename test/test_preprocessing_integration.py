"""
Integration tests for the preprocessing pipeline using real ePI examples
"""

import json
import pytest
from pathlib import Path
from preprocessor.controllers.preprocess_controller import _apply_preprocessing, preprocess_post
from preprocessor.models.fhir_epi import FhirEPI
from preprocessor.models.html_content_manager import get_html_content
from preprocessor.models.html_optimizer import extract_html_classes, optimize_html
from preprocessor.models.html_element_link_manager import list_html_element_links, get_element_classes


# Get the path to test ePIs
TEST_EPI_DIR = Path(__file__).parent / "testing ePIs"


def load_test_epi(filename: str):
    """Load a test ePI bundle from JSON file"""
    filepath = TEST_EPI_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestPreprocessingWithKarvea:
    """Test preprocessing with the Karvea ePI"""
    
    @pytest.fixture
    def karvea_bundle(self):
        """Load Karvea test bundle"""
        return load_test_epi("Bundle-Processedbundlekarvea.json")
    
    def test_load_karvea_bundle(self, karvea_bundle):
        """Test that we can load the Karvea bundle"""
        assert karvea_bundle is not None
        assert karvea_bundle['resourceType'] == 'Bundle'
        assert karvea_bundle['type'] == 'document'
    
    def test_karvea_has_composition_with_html_element_links(self, karvea_bundle):
        """Test that Karvea composition has HtmlElementLink extensions"""
        composition = None
        for entry in karvea_bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'Composition':
                composition = resource
                break
        
        assert composition is not None
        
        # Check for HtmlElementLink extensions
        links = list_html_element_links(composition)
        assert len(links) > 0, "Should have HtmlElementLink extensions"
        
        # Get element classes
        element_classes = get_element_classes(composition)
        print(f"Element classes: {element_classes}")
        
        # Check for specific expected classes
        assert 'pregnancyCategory' in element_classes, "Should have pregnancyCategory"
        assert 'breastfeedingCategory' in element_classes, "Should have breastfeedingCategory"
    
    def test_karvea_composition_html_has_classes(self, karvea_bundle):
        """Test that the Composition text.div contains the expected CSS classes"""
        composition = None
        for entry in karvea_bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'Composition':
                composition = resource
                break
        
        assert composition is not None
        
        # Get HTML content from composition
        html_content = get_html_content(composition)
        assert not html_content.is_empty, "HTML content should not be empty"
        
        # Check if pregnancyCategory appears in raw HTML
        raw_html = html_content.raw_html
        print(f"\nRaw HTML length: {len(raw_html)}")
        print(f"Contains 'pregnancyCategory': {'pregnancyCategory' in raw_html}")
        
        assert 'pregnancyCategory' in raw_html, "Raw HTML should contain pregnancyCategory"
        assert 'breastfeedingCategory' in raw_html, "Raw HTML should contain breastfeedingCategory"
    
    def test_karvea_section_html_has_classes(self, karvea_bundle):
        """Test that section text.div contains the expected CSS classes"""
        composition = None
        for entry in karvea_bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'Composition':
                composition = resource
                break
        
        assert composition is not None
        
        sections = composition.get('section', [])
        assert len(sections) > 0, "Should have sections"
        
        # Check each section for HTML content
        found_pregnancy_in_section = False
        for section in sections:
            section_html = section.get('text', {}).get('div', '')
            if section_html and 'pregnancyCategory' in section_html:
                found_pregnancy_in_section = True
                print(f"Found pregnancyCategory in section: {section.get('title', 'N/A')}")
        
        print(f"Found pregnancyCategory in section HTML: {found_pregnancy_in_section}")
    
    def test_extract_classes_from_karvea_composition(self, karvea_bundle):
        """Test that extract_html_classes finds all classes in Composition HTML"""
        composition = None
        for entry in karvea_bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'Composition':
                composition = resource
                break
        
        html_content = get_html_content(composition)
        raw_html = html_content.raw_html
        
        # Extract classes
        classes = extract_html_classes(raw_html)
        print(f"\nExtracted classes from raw HTML: {classes}")
        
        # These classes should be found
        expected_classes = {'pregnancyCategory', 'breastfeedingCategory', 'lactose'}
        
        for expected_class in expected_classes:
            if expected_class in raw_html:
                assert expected_class in classes, f"Class '{expected_class}' appears in HTML but was not extracted"
    
    def test_extract_classes_from_karvea_section(self, karvea_bundle):
        """Test extracting classes from section HTML"""
        composition = None
        for entry in karvea_bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'Composition':
                composition = resource
                break
        
        sections = composition.get('section', [])
        
        for section in sections:
            section_html = section.get('text', {}).get('div', '')
            if section_html:
                classes = extract_html_classes(section_html)
                print(f"\nSection '{section.get('title', 'N/A')}' classes: {classes}")
                
                # Check if any expected classes are present
                if 'pregnancyCategory' in section_html:
                    assert 'pregnancyCategory' in classes, "pregnancyCategory should be extracted from section"
    
    def test_optimize_preserves_classes(self, karvea_bundle):
        """Test that HTML optimization preserves CSS classes"""
        composition = None
        for entry in karvea_bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'Composition':
                composition = resource
                break
        
        html_content = get_html_content(composition)
        raw_html = html_content.raw_html
        
        # Get classes before optimization
        classes_before = extract_html_classes(raw_html)
        print(f"\nClasses before optimization: {classes_before}")
        
        # Optimize
        optimized_html = optimize_html(raw_html)
        
        # Get classes after optimization
        classes_after = extract_html_classes(optimized_html)
        print(f"Classes after optimization: {classes_after}")
        
        # Check for specific important classes
        important_classes = {'pregnancyCategory', 'breastfeedingCategory', 'lactose'}
        for cls in important_classes:
            if cls in classes_before:
                assert cls in classes_after, f"Optimization removed important class: {cls}"
    
    def test_full_preprocessing_pipeline(self, karvea_bundle):
        """Test the complete preprocessing pipeline"""
        epi = FhirEPI.from_dict(karvea_bundle)
        
        # Get original state
        composition = None
        for entry in karvea_bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'Composition':
                composition = resource
                break
        
        original_links = list_html_element_links(composition)
        original_classes = get_element_classes(composition)
        
        print(f"\nOriginal HtmlElementLinks: {len(original_links)}")
        print(f"Original element classes: {original_classes}")
        
        # Run preprocessing
        preprocessed_epi = _apply_preprocessing(epi)
        preprocessed_dict = preprocessed_epi.to_dict()
        
        # Get preprocessed state
        preprocessed_composition = None
        for entry in preprocessed_dict.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'Composition':
                preprocessed_composition = resource
                break
        
        preprocessed_links = list_html_element_links(preprocessed_composition)
        preprocessed_element_classes = get_element_classes(preprocessed_composition)
        
        print(f"Preprocessed HtmlElementLinks: {len(preprocessed_links)}")
        print(f"Preprocessed element classes: {preprocessed_element_classes}")
        
        # Get the actual HTML to see what classes are present
        html_content = get_html_content(preprocessed_composition)
        actual_html_classes = extract_html_classes(html_content.raw_html)
        print(f"Actual HTML classes after preprocessing: {actual_html_classes}")
        
        # Verify that links are only removed if classes are truly not in HTML
        for cls in original_classes:
            if cls not in preprocessed_element_classes:
                # This class was removed - verify it's not in the HTML
                assert cls not in actual_html_classes, f"Class '{cls}' was removed from extensions but is still in HTML"
            else:
                # This class was kept - it should be in the HTML
                assert cls in actual_html_classes, f"Class '{cls}' is in extensions but not in HTML"


class TestPreprocessingWithFlucelvax:
    """Test preprocessing with the Flucelvax ePI"""
    
    @pytest.fixture
    def flucelvax_bundle(self):
        """Load Flucelvax test bundle"""
        return load_test_epi("Bundle-processedbundleflucelvax.json")
    
    def test_load_flucelvax_bundle(self, flucelvax_bundle):
        """Test that we can load the Flucelvax bundle"""
        assert flucelvax_bundle is not None
        assert flucelvax_bundle['resourceType'] == 'Bundle'
        assert flucelvax_bundle['type'] == 'document'
    
    def test_flucelvax_preprocessing(self, flucelvax_bundle):
        """Test preprocessing Flucelvax ePI"""
        epi = FhirEPI.from_dict(flucelvax_bundle)
        preprocessed_epi = _apply_preprocessing(epi)
        
        assert preprocessed_epi is not None
        assert preprocessed_epi.resource_type == 'Bundle'


class TestPreprocessingAPI:
    """Test the HTTP API endpoint"""
    
    def test_preprocess_post_with_karvea(self):
        """Test the POST endpoint with Karvea bundle"""
        karvea_bundle = load_test_epi("Bundle-Processedbundlekarvea.json")
        
        result, status_code = preprocess_post(body=karvea_bundle)
        
        assert status_code == 200
        assert 'error' not in result
        assert result['resourceType'] == 'Bundle'
    
    def test_preprocess_post_with_none_body(self):
        """Test the POST endpoint with no body"""
        result, status_code = preprocess_post(body=None)
        
        assert status_code == 400
        assert 'error' in result
    
    def test_preprocess_post_with_invalid_resource_type(self):
        """Test the POST endpoint with invalid resource type"""
        invalid_bundle = {'resourceType': 'Patient', 'type': 'document'}
        result, status_code = preprocess_post(body=invalid_bundle)
        
        assert status_code == 400
        assert 'error' in result
