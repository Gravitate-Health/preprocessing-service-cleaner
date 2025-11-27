import connexion
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
    validate_content_integrity
)
from preprocessor.models.html_element_link_cleanup import (
    cleanup_unused_html_element_links
)


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


def _apply_preprocessing(epi: FhirEPI) -> FhirEPI:
    """Apply preprocessing transformations to the ePI
    
    Business logic:
    1. Extract and optimize HTML content (remove non-functional tags, simplify nested structures)
    2. Extract all CSS classes used in the optimized HTML
    3. Remove HtmlElementLink extensions that reference unused classes
    
    :param epi: The input FHIR ePI
    :return: The preprocessed FHIR ePI
    """
    # Work with the dict representation for easier manipulation
    epi_dict = epi.to_dict()
    
    # Statistics for logging/debugging
    stats = {
        'compositions_processed': 0,
        'html_optimizations': 0,
        'links_removed': 0,
        'validation_failures': 0
    }
    
    # Process each entry in the bundle
    if 'entry' in epi_dict:
        for entry in epi_dict.get('entry', []):
            resource = entry.get('resource', {})
            
            # Only process Composition resources
            if resource.get('resourceType') == 'Composition':
                stats['compositions_processed'] += 1
                
                # Step 1: Extract and optimize HTML content
                original_html = get_html_content(resource)
                
                if original_html:
                    # Optimize the HTML
                    optimized_html = optimize_html(original_html)
                    
                    # Validate content integrity
                    if validate_content_integrity(original_html, optimized_html):
                        # Update the composition with optimized HTML
                        update_html_content(resource, optimized_html)
                        stats['html_optimizations'] += 1
                        
                        # Step 2: Extract CSS classes from optimized HTML
                        html_classes = extract_html_classes(optimized_html)
                        
                        # Step 3: Remove unused HtmlElementLink extensions
                        cleanup_stats = cleanup_unused_html_element_links(resource, html_classes)
                        stats['links_removed'] += cleanup_stats.get('removed', 0)
                    else:
                        stats['validation_failures'] += 1
                        print(f"Warning: HTML optimization validation failed for composition. Keeping original.")
    
    # Log statistics (in production, use proper logging)
    print(f"Preprocessing complete: {stats}")
    
    # Convert back to FhirEPI model
    return FhirEPI.from_dict(epi_dict)
