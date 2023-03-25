class KorException(Exception):
    """Base class for all Kor exceptions."""


class ParseError(KorException):
    """Exception for parsing errors."""


class ValidationError(KorException):
    """Exception for validators."""
