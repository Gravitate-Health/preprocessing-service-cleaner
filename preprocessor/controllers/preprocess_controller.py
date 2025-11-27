import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from preprocessor import util
from preprocessor.models.fhir_epi import FhirEPI


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
    
    :param epi: The input FHIR ePI
    :return: The preprocessed FHIR ePI
    """
    # Create a copy of the ePI to avoid modifying the input
    processed_epi = FhirEPI(
        resource_type=epi.resource_type,
        type=epi.type,
        timestamp=epi.timestamp,
        entry=epi.entry.copy() if epi.entry else [],
        meta=epi.meta,
        identifier=epi.identifier,
        signature=epi.signature
    )
    
    # Example preprocessing steps:
    # 1. Validate all entries
    # 2. Normalize formatting
    # 3. Apply business rules
    # 4. Enhance metadata
    
    # Placeholder for actual preprocessing logic
    # You can add specific transformations here
    
    return processed_epi
