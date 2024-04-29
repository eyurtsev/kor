import asyncio
from typing import List

import pytest
from langchain_core.documents import Document

from kor import (
    DocumentExtraction,
    Object,
    Text,
    create_extraction_chain,
    extract_from_documents,
)

from ..utils import ToyChatModel

SIMPLE_TEXT_SCHEMA = Text(
    id="text_node",
    description="Text Field",
    many=False,
    examples=[("hello", "goodbye")],
)
SIMPLE_OBJECT_SCHEMA = Object(id="obj", description="", attributes=[SIMPLE_TEXT_SCHEMA])


@pytest.mark.parametrize(
    "use_uid,expected_results",
    [
        (
            True,
            [
                {
                    "data": {"obj": {"text_node": "hello"}},
                    "errors": [],
                    "raw": '<json>{ "obj": { "text_node": "hello" } }</json>',
                    "source_uid": "a",
                    "uid": "a",
                    "validated_data": {},
                },
                {
                    "data": {"obj": {"text_node": "hello"}},
                    "errors": [],
                    "raw": '<json>{ "obj": { "text_node": "hello" } }</json>',
                    "source_uid": "b",
                    "uid": "b",
                    "validated_data": {},
                },
            ],
        ),
        (
            False,
            [
                {
                    "data": {"obj": {"text_node": "hello"}},
                    "errors": [],
                    "raw": '<json>{ "obj": { "text_node": "hello" } }</json>',
                    "source_uid": "0",
                    "uid": "0",
                    "validated_data": {},
                },
                {
                    "data": {"obj": {"text_node": "hello"}},
                    "errors": [],
                    "raw": '<json>{ "obj": { "text_node": "hello" } }</json>',
                    "source_uid": "1",
                    "uid": "1",
                    "validated_data": {},
                },
            ],
        ),
    ],
)
def test_extract_from_documents(
    use_uid: bool, expected_results: List[DocumentExtraction]
) -> None:
    """Test extract_from_documents."""
    chain = create_extraction_chain(
        ToyChatModel(response='<json>{ "obj": { "text_node": "hello" } }</json>'),
        SIMPLE_OBJECT_SCHEMA,
        encoder_or_encoder_class="json",
    )
    documents = [
        Document(page_content="hello", metadata={"uid": "a"}),
        Document(page_content="goodbye", metadata={"uid": "b"}),
    ]

    extraction_results = asyncio.run(
        extract_from_documents(
            chain,
            documents,
            use_uid=use_uid,
            max_concurrency=100,
        )
    )
    assert extraction_results == expected_results


def test_extract_from_documents_with_extraction_uid_function() -> None:
    """Verify that the uid is getting assigned correctly."""
    chain = create_extraction_chain(
        ToyChatModel(response='<json>{ "obj": { "text_node": "hello" } }</json>'),
        SIMPLE_OBJECT_SCHEMA,
        encoder_or_encoder_class="json",
    )
    documents = [
        Document(page_content="hello", metadata={"uid": "a"}),
    ]

    def uid_function(doc: Document) -> str:
        """Function to assign a uid to the extraction."""
        return doc.metadata["uid"] + "!"

    extraction_results = asyncio.run(
        extract_from_documents(
            chain,
            documents,
            extraction_uid_function=uid_function,
            max_concurrency=100,
        )
    )
    first_result = extraction_results[0]
    assert isinstance(first_result, dict)
    assert first_result["uid"] == "a!"


def test_check_assertion_is_raised_when_using_missing_uuid() -> None:
    """Verify that the uid is getting assigned correctly."""
    chain = create_extraction_chain(
        ToyChatModel(response='<json>{ "obj": { "text_node": "hello" } }</json>'),
        SIMPLE_OBJECT_SCHEMA,
        encoder_or_encoder_class="json",
    )
    documents = [Document(page_content="hello")]

    with pytest.raises(ValueError):
        asyncio.run(
            extract_from_documents(
                chain,
                documents,
                use_uid=True,
                max_concurrency=100,
            )
        )
