"""Light-weight tests to catch some changes in the public interface."""
from kor import __all__


def test_kor__all__() -> None:
    """Hard-code contents of __all__.

    Upon changes this may help serve as a reminder to correctly bump the semver.
    """
    assert sorted(__all__) == [
        "Bool",
        "BulletPointDescriptor",
        "CSVEncoder",
        "DocumentExtraction",
        "Extraction",
        "JSONEncoder",
        "Number",
        "Object",
        "Option",
        "Selection",
        "Text",
        "TypeDescriptor",
        "TypeScriptDescriptor",
        "XMLEncoder",
        "__version__",
        "create_extraction_chain",
        "extract_from_documents",
        "from_pydantic",
    ]
