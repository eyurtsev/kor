"""Extraction building blocks."""
import dataclasses
from kor.elements import ExtractionInput


@dataclasses.dataclass(frozen=True, kw_only=True)
class TimePeriod(ExtractionInput):
    """Built-in for more general time-periods; e.g., 'after dinner', 'next year'"""


@dataclasses.dataclass(frozen=True, kw_only=True)
class NumericRange(ExtractionInput):
    """Built-in numeric range input."""
