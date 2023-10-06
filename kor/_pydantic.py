"""Internal code used to support Pydantic v1 and v2."""


def _get_pydantic_major_version() -> int:
    """Get the major version of Pydantic."""
    try:
        import pydantic

        return int(pydantic.__version__.split(".")[0])
    except ImportError:
        return 0


PYDANTIC_MAJOR_VERSION = _get_pydantic_major_version()
