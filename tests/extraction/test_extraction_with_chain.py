"""Test that the extraction chain works as expected."""
from typing import Any, Mapping, Optional

import langchain
import pytest
from langchain import PromptTemplate
from langchain.chains import LLMChain

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
        assert isinstance(chain, LLMChain)
        # Try to run through predict and parse
        chain.run("some string")


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
    assert isinstance(chain, LLMChain)
    # Try to run through predict and parse
    chain.run("some string")


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


@pytest.mark.parametrize("verbose", [True, False, None])
def test_instantiation_with_verbose_flag(verbose: Optional[bool]) -> None:
    """Create an extraction chain."""
    chat_model = ToyChatModel(response="hello")
    chain = create_extraction_chain(
        chat_model,
        SIMPLE_OBJECT_SCHEMA,
        encoder_or_encoder_class="json",
        verbose=verbose,
    )
    assert isinstance(chain, LLMChain)
    if verbose is None:
        expected_verbose = langchain.verbose
    else:
        expected_verbose = verbose
    assert chain.verbose == expected_verbose


def test_using_custom_template() -> None:
    """Create an extraction chain with a custom template."""
    template = PromptTemplate(
        input_variables=["format_instructions", "type_description"],
        template=(
            "custom_prefix\n"
            "{type_description}\n\n"
            "{format_instructions}\n"
            "custom_suffix"
        ),
    )
    chain = create_extraction_chain(
        ToyChatModel(response="hello"),
        OBJECT_SCHEMA_WITH_MANY,
        instruction_template=template,
        encoder_or_encoder_class="json",
    )
    prompt_value = chain.prompt.format_prompt(text="hello")
    system_message = prompt_value.to_messages()[0]
    string_value = prompt_value.to_string()

    assert "custom_prefix" in string_value
    assert "custom_suffix" in string_value
    assert "custom_prefix" in system_message.content
    assert "custom_suffix" in system_message.content
