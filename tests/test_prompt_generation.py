import pytest

from kor import JSONEncoder, Object, TypeScriptDescriptor
from kor.encoders import InputFormatter
from kor.prompts import create_langchain_prompt


@pytest.mark.parametrize(
    "input_formatter, expected_string",
    [
        (None, "user input"),
        ("triple_quotes", '"""\nuser input\n"""'),
        ("text_prefix", 'Text: """\nuser input\n"""'),
    ],
)
def test_input_formatter_applied_correctly(
    input_formatter: InputFormatter, expected_string: str
) -> None:
    untyped_object = Object(
        id="obj",
        examples=[("text", {"text": "text"})],
        attributes=[],
    )
    prompt = create_langchain_prompt(
        untyped_object,
        JSONEncoder(),
        TypeScriptDescriptor(),
        input_formatter=input_formatter,
    )

    prompt_value = prompt.format_prompt(text="user input")

    assert prompt_value.to_messages()[-1].content == expected_string
    assert expected_string in prompt_value.to_string()
