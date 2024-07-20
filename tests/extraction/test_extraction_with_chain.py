"""Test that the extraction chain works as expected."""
from typing import Any, Mapping, Optional

import pytest
from langchain_core.runnables import Runnable

from kor.encoders import CSVEncoder, JSONEncoder
from kor.extraction import create_extraction_chain
from kor.nodes import Object, Text
from tests.utils import ToyChatModel

SIMPLE_TEXT_SCHEMA = Text(
    id="text_node",
    description="Text Field",
    many=False,
    examples=[("hello", "goodbye")],
)
SIMPLE_OBJECT_SCHEMA = Object(id="obj", description="", attributes=[SIMPLE_TEXT_SCHEMA])


@pytest.mark.parametrize(
    "options",
    [
        {"encoder_or_encoder_class": "csv", "input_formatter": None},
        {"encoder_or_encoder_class": "csv", "input_formatter": "text_prefix"},
        {"encoder_or_encoder_class": "json"},
        {"encoder_or_encoder_class": "json", "ensure_ascii": False},
        {"encoder_or_encoder_class": "json", "ensure_ascii": True},
        {"encoder_or_encoder_class": "xml"},
        {"encoder_or_encoder_class": JSONEncoder()},
        {"encoder_or_encoder_class": JSONEncoder},
        {"encoder_or_encoder_class": CSVEncoder},
    ],
)
def test_create_extraction_chain(options: Mapping[str, Any]) -> None:
    """Create an extraction chain."""
    chat_model = ToyChatModel(response="hello")

    for schema in [SIMPLE_OBJECT_SCHEMA]:
        chain = create_extraction_chain(chat_model, schema, **options)
        assert isinstance(chain, Runnable)
        # Try to run through predict and parse
        chain.invoke("some string")  # type: ignore


@pytest.mark.parametrize(
    "options",
    [
        {"encoder_or_encoder_class": CSVEncoder, "node": SIMPLE_OBJECT_SCHEMA},
        {
            "encoder_or_encoder_class": CSVEncoder(SIMPLE_OBJECT_SCHEMA),
            "node": SIMPLE_OBJECT_SCHEMA,
        },
    ],
)
def test_create_extraction_chain_with_csv_encoder(options: Mapping[str, Any]) -> None:
    """Create an extraction chain."""
    chat_model = ToyChatModel(response="hello")

    chain = create_extraction_chain(chat_model, **options)
    assert isinstance(chain, Runnable)
    # Try to run through predict and parse
    chain.invoke("some string")  # type: ignore


MANY_TEXT_SCHEMA = Text(
    id="text_node",
    description="Text Field",
    many=True,
    examples=[("hello", "goodbye")],
)


OBJECT_SCHEMA_WITH_MANY = Object(
    id="obj", description="", attributes=[MANY_TEXT_SCHEMA]
)


OBJECT_SCHEMA_WITH_NESTED_OBJECT = Object(
    id="obj",
    description="",
    attributes=[Object(id="nested", attributes=[SIMPLE_TEXT_SCHEMA])],
)


@pytest.mark.parametrize(
    "options",
    [
        # Not supporting embedded lists yet
        {"encoder_or_encoder_class": CSVEncoder, "node": OBJECT_SCHEMA_WITH_MANY},
        # Not supporting nested objects yet
        {
            "encoder_or_encoder_class": CSVEncoder,
            "node": OBJECT_SCHEMA_WITH_NESTED_OBJECT,
        },
    ],
)
def test_not_implemented_assertion_raised_for_csv(options: Mapping[str, Any]) -> None:
    """Create an extraction chain."""
    chat_model = ToyChatModel(response="hello")

    with pytest.raises(NotImplementedError):
        create_extraction_chain(chat_model, **options)


@pytest.mark.parametrize("verbose", [True, False])
def test_instantiation_with_verbose_flag(verbose: Optional[bool]) -> None:
    """Create an extraction chain."""
    chat_model = ToyChatModel(response="hello")
    with pytest.raises(NotImplementedError):
        create_extraction_chain(
            chat_model,
            SIMPLE_OBJECT_SCHEMA,
            encoder_or_encoder_class="json",
            verbose=verbose,
        )


def test_get_prompt() -> None:
    """Create an extraction chain."""
    chat_model = ToyChatModel(response="hello")
    chain = create_extraction_chain(
        chat_model,
        SIMPLE_OBJECT_SCHEMA,
        encoder_or_encoder_class="json",
    )
    prompts = chain.get_prompts()
    prompt = prompts[0]
    assert prompt.format_prompt(text="[text]").to_string() == (
        "Your goal is to extract structured information from the user's input that "
        "matches the form described below. When extracting information please make "
        "sure it matches the type information exactly. Do not add any attributes that "
        "do not appear in the schema shown below.\n"
        "\n"
        "```TypeScript\n"
        "\n"
        "obj: { // \n"
        " text_node: string // Text Field\n"
        "}\n"
        "```\n"
        "\n"
        "\n"
        "Please output the extracted information in JSON format. Do not output "
        "anything except for the extracted information. Do not add any clarifying "
        "information. Do not add any fields that are not in the schema. If the text "
        "contains attributes that do not appear in the schema, please ignore them. "
        "All output must be in JSON format and follow the schema specified above. "
        "Wrap the JSON in <json> tags.\n"
        "\n"
        "\n"
        "\n"
        "Input: hello\n"
        'Output: <json>{"obj": {"text_node": "goodbye"}}</json>\n'
        "Input: [text]\n"
        "Output:"
    )
