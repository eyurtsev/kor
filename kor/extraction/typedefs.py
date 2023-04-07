"""Type definitions for the extraction package."""
from typing import Any, Dict, List, TypedDict


class Extraction(TypedDict):
    """Type-definition for an extraction result."""

    raw: str
    """The raw output from the LLM."""
    data: Dict[str, Any]
    """The decoding of the raw output from the LLM without any further processing."""
    validated_data: Dict[str, Any]
    """The validated data if a validator was provided."""
    errors: List[Exception]
    """Any errors encountered during decoding or validation."""


class DocumentExtraction(Extraction):
    """Type-definition for a document extraction result.

    The original extraction typedefs together with the unique identifiers for the result
    itself as well as the source document.

    Identifiers are included to make it easier to link the extraction result
    to the source content.
    """

    uid: str
    """The uid of the extraction result."""
    source_uid: str
    """The source uid of the document from which data was extracted."""
