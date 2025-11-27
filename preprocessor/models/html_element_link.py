"""
HtmlElementLink Extension Model

Represents the HtmlElementLink extension used for annotating HTML elements
in ePI Composition resources.

Reference:
  http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink
"""

from typing import Optional, Dict, Any


class Coding:
    """FHIR Coding representation for concepts"""

    def __init__(
        self,
        system: Optional[str] = None,
        code: Optional[str] = None,
        display: Optional[str] = None,
    ):
        self.system = system
        self.code = code
        self.display = display

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Coding":
        """Create from dictionary"""
        if not data:
            return cls()
        return cls(
            system=data.get("system"),
            code=data.get("code"),
            display=data.get("display"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        if self.system:
            result["system"] = self.system
        if self.code:
            result["code"] = self.code
        if self.display:
            result["display"] = self.display
        return result

    def __eq__(self, other):
        if not isinstance(other, Coding):
            return False
        return (
            self.system == other.system
            and self.code == other.code
            and self.display == other.display
        )

    def __repr__(self):
        return f"Coding(system={self.system}, code={self.code}, display={self.display})"


class CodeableReference:
    """FHIR CodeableReference for concept representation"""

    def __init__(self, codings: Optional[list] = None):
        """Initialize with list of Coding objects or empty"""
        self.codings = codings or []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeableReference":
        """Create from dictionary"""
        if not data:
            return cls()

        codings = []
        concept_data = data.get("concept", {})
        coding_list = concept_data.get("coding", [])

        for coding_dict in coding_list:
            codings.append(Coding.from_dict(coding_dict))

        return cls(codings=codings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        if not self.codings:
            return {"concept": {"coding": []}}

        return {
            "concept": {"coding": [coding.to_dict() for coding in self.codings]}
        }

    def __eq__(self, other):
        if not isinstance(other, CodeableReference):
            return False
        return self.codings == other.codings

    def __repr__(self):
        return f"CodeableReference(codings={self.codings})"


class HtmlElementLink:
    """
    HtmlElementLink Extension

    Represents an annotation linking HTML elements to clinical concepts.

    Attributes:
        element_class (str): The HTML element class being annotated
                           Examples: pregnancyCategory, indication, liver, etc.
        concept (CodeableReference): The clinical concept being referenced
    """

    STRUCTURE_DEFINITION_URL = (
        "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/HtmlElementLink"
    )

    def __init__(
        self,
        element_class: Optional[str] = None,
        concept: Optional[CodeableReference] = None,
    ):
        self.element_class = element_class
        self.concept = concept or CodeableReference()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HtmlElementLink":
        """
        Create HtmlElementLink from dictionary representation

        Args:
            data: Dictionary with 'extension' key containing the extension data

        Returns:
            HtmlElementLink instance
        """
        if not data:
            return cls()

        # Handle both direct extension data and wrapped format
        extension_list = data.get("extension", [])

        element_class = None
        concept = None

        for ext in extension_list:
            url = ext.get("url")
            if url == "elementClass":
                element_class = ext.get("valueString")
            elif url == "concept":
                concept_dict = ext.get("valueCodeableReference", {})
                concept = CodeableReference.from_dict(concept_dict)

        return cls(element_class=element_class, concept=concept)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to FHIR extension dictionary format

        Returns:
            Dictionary with extension structure
        """
        extension_list = []

        if self.element_class:
            extension_list.append(
                {"url": "elementClass", "valueString": self.element_class}
            )

        if self.concept:
            extension_list.append(
                {
                    "url": "concept",
                    "valueCodeableReference": self.concept.to_dict(),
                }
            )

        return {
            "extension": extension_list,
            "url": self.STRUCTURE_DEFINITION_URL,
        }

    def __eq__(self, other):
        if not isinstance(other, HtmlElementLink):
            return False
        return (
            self.element_class == other.element_class
            and self.concept == other.concept
        )

    def __repr__(self):
        return f"HtmlElementLink(element_class={self.element_class}, concept={self.concept})"

    def __str__(self):
        concept_str = ""
        if self.concept and self.concept.codings:
            displays = [c.display or c.code for c in self.concept.codings]
            concept_str = f" → {', '.join(displays)}"
        return f"{self.element_class}{concept_str}"
