import connexion
import os
from typing import Dict
from typing import Tuple
from typing import Union

from preprocessor import util
from preprocessor.models.fhir_epi import FhirEPI
from preprocessor.models.html_element_link import HtmlElementLink
from preprocessor.models.html_content_manager import (
    get_html_content,
    update_html_content
)
from preprocessor.models.html_optimizer import (
    optimize_html,
    extract_html_classes,
    validate_content_integrity,
    cleanup_html_styles_and_classes
)
from preprocessor.models.html_element_link_cleanup import (
    cleanup_unused_html_element_links
)

# Feature flags from environment variables
ENABLE_HTML_OPTIMIZATION = os.getenv('ENABLE_HTML_OPTIMIZATION', 'true').lower() in ('true', '1', 'yes', 'on')
ENABLE_LINK_CLEANUP = os.getenv('ENABLE_LINK_CLEANUP', 'true').lower() in ('true', '1', 'yes', 'on')
ENABLE_STYLE_CLEANUP = os.getenv('ENABLE_STYLE_CLEANUP', 'true').lower() in ('true', '1', 'yes', 'on')


def preprocess_post(body=None):  # noqa: E501
    """preprocess_post

    Preprocesses an ePI. Receives an ePI and returns it preprocessed. # noqa: E501

    :param body: ePI to preprocess.
    :type body: dict

    :rtype: Union[dict, Tuple[dict, int], Tuple[dict, int, Dict[str, str]]
    """
    try:
        # Parse the incoming FHIR ePI bundle
        if body is None:
            return {'error': 'Request body is required'}, 400
        
        # Convert dict to FhirEPI model instance
        epi = FhirEPI.from_dict(body)
        
        # Validate the ePI structure
        if epi.resource_type != 'Bundle':
            return {'error': 'Invalid FHIR resource type. Expected Bundle.'}, 400
        
        if epi.type != 'document':
            return {'error': 'Invalid Bundle type. Expected document.'}, 400
        
        # TODO: Implement preprocessing logic here
        # This is where you would apply transformations, validations, 
        # and modifications to the ePI content
        preprocessed_epi = _apply_preprocessing(epi)
        
        # Return the preprocessed ePI as a dictionary
        return preprocessed_epi.to_dict(), 200
    
    except Exception as e:
        return {'error': f'Failed to process ePI: {str(e)}'}, 500


def _process_sections_recursively(sections, stats):
    """Process sections and subsections recursively
    
    :param sections: List of section dictionaries
    :param stats: Statistics dictionary to update
    """
    for section in sections:
        # Process HTML content in this section
        html_content = get_html_content(section)
        
        if html_content and not html_content.is_empty:
            if ENABLE_HTML_OPTIMIZATION:
                # Optimize the HTML
                optimized_html = optimize_html(html_content.raw_html)
                
                # Validate content integrity
                if validate_content_integrity(html_content.raw_html, optimized_html):
                    # Update the section with optimized HTML
                    update_html_content(section, optimized_html)
                    stats['html_optimizations'] += 1
                else:
                    stats['validation_failures'] += 1
                    print(f"Warning: HTML optimization validation failed for section '{section.get('title', 'N/A')}'. Keeping original.")
            else:
                stats['html_optimizations_skipped'] = stats.get('html_optimizations_skipped', 0) + 1
        
        # Process subsections recursively
        if 'section' in section:
            _process_sections_recursively(section['section'], stats)


def _collect_all_html_classes_from_resource(resource):
    """Collect all CSS classes from a resource and all its sections/subsections
    
    :param resource: FHIR resource dictionary
    :return: Set of all CSS class names found
    """
    all_classes = set()
    
    # Get classes from resource text.div
    html_content = get_html_content(resource)
    if html_content and not html_content.is_empty:
        all_classes.update(extract_html_classes(html_content.raw_html))
    
    # Recursively get classes from sections
    def collect_from_sections(sections):
        classes = set()
        for section in sections:
            # Get classes from section text.div
            section_html = get_html_content(section)
            if section_html and not section_html.is_empty:
                classes.update(extract_html_classes(section_html.raw_html))
            
            # Process subsections
            if 'section' in section:
                classes.update(collect_from_sections(section['section']))
        return classes
    
    if 'section' in resource:
        all_classes.update(collect_from_sections(resource['section']))
    
    return all_classes


def _apply_preprocessing(epi: FhirEPI) -> FhirEPI:
    """Apply preprocessing transformations to the ePI
    
    Business logic:
    1. Extract and optimize HTML content (remove non-functional tags, simplify nested structures) - controlled by ENABLE_HTML_OPTIMIZATION
    2. Extract all CSS classes used in the optimized HTML (from all sections recursively)
    3. Remove HtmlElementLink extensions that reference unused classes - controlled by ENABLE_LINK_CLEANUP
    
    :param epi: The input FHIR ePI
    :return: The preprocessed FHIR ePI
    """
    # Work with the dict representation for easier manipulation
    epi_dict = epi.to_dict()
    
    # Statistics for logging/debugging
    stats = {
        'html_optimizations': 0,
        'html_optimizations_skipped': 0,
        'links_removed': 0,
        'validation_failures': 0,
        'styles_cleaned': 0
    }
    
    # Log feature flags
    print(f"Feature flags: HTML_OPTIMIZATION={'enabled' if ENABLE_HTML_OPTIMIZATION else 'disabled'}, "
          f"LINK_CLEANUP={'enabled' if ENABLE_LINK_CLEANUP else 'disabled'}, "
          f"STYLE_CLEANUP={'enabled' if ENABLE_STYLE_CLEANUP else 'disabled'}")
    
    # Process each entry in the bundle
    if 'entry' in epi_dict:
        for entry in epi_dict.get('entry', []):
            resource = entry.get('resource', {})
            
            # Process top-level resource HTML content
            html_content = get_html_content(resource)
            
            if html_content and not html_content.is_empty:
                if ENABLE_HTML_OPTIMIZATION:
                    # Optimize the HTML
                    optimized_html = optimize_html(html_content.raw_html)
                    
                    # Validate content integrity
                    if validate_content_integrity(html_content.raw_html, optimized_html):
                        # Update the resource with optimized HTML
                        update_html_content(resource, optimized_html)
                        stats['html_optimizations'] += 1
                    else:
                        stats['validation_failures'] += 1
                        print(f"Warning: HTML optimization validation failed for resource {resource.get('resourceType')}. Keeping original.")
                else:
                    stats['html_optimizations_skipped'] += 1
            
            # Process sections recursively
            if 'section' in resource:
                _process_sections_recursively(resource['section'], stats)
            
            # For Composition resources, collect ALL classes from all sections and clean up links
            if resource.get('resourceType') == 'Composition':
                # Collect classes from the entire resource tree
                all_html_classes = _collect_all_html_classes_from_resource(resource)
                
                if ENABLE_LINK_CLEANUP:
                    # Remove unused HtmlElementLink extensions
                    cleanup_stats = cleanup_unused_html_element_links(resource, all_html_classes)
                    stats['links_removed'] += cleanup_stats.get('removed', 0)
                
                if ENABLE_STYLE_CLEANUP:
                    # Get allowed classes from HtmlElementLink extensions
                    allowed_classes = set()
                    for extension in resource.get('extension', []):
                        if extension.get('url') == 'http://hl7.org/fhir/StructureDefinition/HtmlElementLink':
                            for ext_detail in extension.get('extension', []):
                                if ext_detail.get('url') == 'elementClass':
                                    allowed_classes.add(ext_detail.get('valueString', ''))
                    
                    # Clean up styles and classes in the resource tree
                    def cleanup_styles_in_sections(sections):
                        for section in sections:
                            html_content = get_html_content(section)
                            if html_content and not html_content.is_empty:
                                cleaned_html = cleanup_html_styles_and_classes(html_content.raw_html, allowed_classes)
                                if cleaned_html != html_content.raw_html:
                                    update_html_content(section, cleaned_html)
                                    stats['styles_cleaned'] += 1
                            
                            if 'section' in section:
                                cleanup_styles_in_sections(section['section'])
                    
                    # Clean resource-level HTML
                    html_content = get_html_content(resource)
                    if html_content and not html_content.is_empty:
                        cleaned_html = cleanup_html_styles_and_classes(html_content.raw_html, allowed_classes)
                        if cleaned_html != html_content.raw_html:
                            update_html_content(resource, cleaned_html)
                            stats['styles_cleaned'] += 1
                    
                    # Clean sections recursively
                    if 'section' in resource:
                        cleanup_styles_in_sections(resource['section'])
    
    # Log statistics (in production, use proper logging)
    print(f"Preprocessing complete: {stats}")
    
    # Convert back to FhirEPI model
    return FhirEPI.from_dict(epi_dict)
