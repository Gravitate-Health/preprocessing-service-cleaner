"""
FHIR ePI (electronic Product Information) Model

Represents a FHIR Bundle containing an electronic Product Information document
(Composition resource) with associated resources.
"""

import typing
from preprocessor.models.base_model import Model


class FhirEPI(Model):
    """FHIR Bundle representing an electronic Product Information (ePI)
    
    This model represents a complete ePI as a FHIR Bundle that contains:
    - A Composition resource describing the document
    - Referenced resources (Medication, Organization, etc.)
    """
    
    openapi_types: typing.Dict[str, type] = {
        'resource_type': str,
        'type': str,
        'timestamp': str,
        'entry': list,
        'meta': dict,
        'identifier': dict,
        'signature': dict,
    }

    attribute_map: typing.Dict[str, str] = {
        'resource_type': 'resourceType',
        'type': 'type',
        'timestamp': 'timestamp',
        'entry': 'entry',
        'meta': 'meta',
        'identifier': 'identifier',
        'signature': 'signature',
    }

    def __init__(
        self,
        resource_type: str = None,
        type: str = None,
        timestamp: str = None,
        entry: list = None,
        meta: dict = None,
        identifier: dict = None,
        signature: dict = None,
    ):
        """Initialize a FHIR ePI Bundle
        
        :param resource_type: FHIR resourceType (should be 'Bundle')
        :param type: Bundle type (typically 'document')
        :param timestamp: Timestamp when the bundle was created (ISO 8601)
        :param entry: List of bundle entries containing resources
        :param meta: Metadata about the resource
        :param identifier: Identifier for the bundle
        :param signature: Digital signature of the bundle
        """
        self.resource_type = resource_type or 'Bundle'
        self.type = type or 'document'
        self.timestamp = timestamp
        self.entry = entry or []
        self.meta = meta
        self.identifier = identifier
        self.signature = signature

    @classmethod
    def from_dict(cls, dikt: dict) -> 'FhirEPI':
        """Create a FhirEPI instance from a dictionary
        
        :param dikt: Dictionary representation of the ePI
        :return: FhirEPI instance
        """
        instance = cls()
        
        if dikt is None:
            return instance
        
        # Map dictionary keys to model attributes
        if 'resourceType' in dikt:
            instance.resource_type = dikt.get('resourceType')
        if 'type' in dikt:
            instance.type = dikt.get('type')
        if 'timestamp' in dikt:
            instance.timestamp = dikt.get('timestamp')
        if 'entry' in dikt:
            instance.entry = dikt.get('entry') or []
        if 'meta' in dikt:
            instance.meta = dikt.get('meta')
        if 'identifier' in dikt:
            instance.identifier = dikt.get('identifier')
        if 'signature' in dikt:
            instance.signature = dikt.get('signature')
        
        return instance

    def to_dict(self) -> dict:
        """Convert the FhirEPI instance to a dictionary
        
        :return: Dictionary representation of the ePI
        """
        result = {}
        
        if self.resource_type is not None:
            result['resourceType'] = self.resource_type
        if self.type is not None:
            result['type'] = self.type
        if self.timestamp is not None:
            result['timestamp'] = self.timestamp
        if self.entry is not None and len(self.entry) > 0:
            result['entry'] = self.entry
        if self.meta is not None:
            result['meta'] = self.meta
        if self.identifier is not None:
            result['identifier'] = self.identifier
        if self.signature is not None:
            result['signature'] = self.signature
        
        return result

    def __repr__(self) -> str:
        """Return string representation of FhirEPI"""
        return f"FhirEPI(resourceType={self.resource_type}, type={self.type}, entries={len(self.entry)})"

    def __str__(self) -> str:
        """Return string representation of FhirEPI"""
        return self.__repr__()

    def get_composition(self) -> dict:
        """Get the Composition resource from the bundle
        
        The first entry is typically the Composition resource in a document bundle.
        
        :return: Composition resource dict or None
        """
        if not self.entry or len(self.entry) == 0:
            return None
        
        first_entry = self.entry[0]
        if isinstance(first_entry, dict) and 'resource' in first_entry:
            resource = first_entry['resource']
            if isinstance(resource, dict) and resource.get('resourceType') == 'Composition':
                return resource
        
        return None

    def get_entries_by_resource_type(self, resource_type: str) -> list:
        """Get all entries of a specific resource type
        
        :param resource_type: The FHIR resourceType to filter by
        :return: List of entries matching the resource type
        """
        matching = []
        for entry in self.entry:
            if isinstance(entry, dict) and 'resource' in entry:
                resource = entry['resource']
                if isinstance(resource, dict) and resource.get('resourceType') == resource_type:
                    matching.append(entry)
        
        return matching
