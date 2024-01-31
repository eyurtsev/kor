"""Code to dynamically generate appropriate LLM prompts."""
from __future__ import annotations

from typing import Any, List, Optional, Tuple

from langchain.prompts import BasePromptTemplate, PromptTemplate
from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    PromptValue,
    SystemMessage,
)

from kor.encoders import Encoder
from kor.encoders.encode import InputFormatter, encode_examples, format_text
from kor.examples import generate_examples
from kor.extraction.parser import KorParser
from kor.nodes import Object
from kor.type_descriptors import TypeDescriptor

try:
    # Use pydantic v1 namespace since working with langchain
    from pydantic.v1 import Extra  # type: ignore[assignment]
except ImportError:
    from pydantic import Extra  # type: ignore[assignment]

from .validators import Validator

DEFAULT_INSTRUCTION_TEMPLATE = PromptTemplate(
    input_variables=["type_description", "format_instructions"],
    template=(
        "Your goal is to extract structured information from the user's input that"
        " matches the form described below. When extracting information please make"
        " sure it matches the type information exactly. Do not add any attributes that"
        " do not appear in the schema shown below.\n\n"
        "{type_description}\n\n"
        "{format_instructions}\n\n"
    ),
)


class ExtractionPromptValue(PromptValue):
    """Integration with langchain prompt format."""

    string: str
    messages: List[BaseMessage]

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def to_string(self) -> str:
        """Format the prompt to a string."""
        return self.string

    def to_messages(self) -> List[BaseMessage]:
        """Get materialized messages."""
        return self.messages


class ExtractionPromptTemplate(BasePromptTemplate):
    """Extraction prompt template."""

    encoder: Encoder
    node: Object
    type_descriptor: TypeDescriptor
    input_formatter: InputFormatter
    instruction_template: PromptTemplate

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def format_prompt(  # type: ignore[override]
        self,
        text: str,
    ) -> PromptValue:
        """Format the prompt."""
        text = format_text(text, input_formatter=self.input_formatter)
        return ExtractionPromptValue(
            string=self.to_string(text), messages=self.to_messages(text)
        )

    def format(self, **kwargs: Any) -> str:
        """Implementation of deprecated format method."""
        raise NotImplementedError()

    @property
    def _prompt_type(self) -> str:
        """Prompt type."""
        return "ExtractionPromptTemplate"

    def to_string(self, text: str) -> str:
        """Format the template to a string."""
        instruction_segment = self.format_instruction_segment(self.node)
        encoded_examples = self.generate_encoded_examples(self.node)
        formatted_examples: List[str] = []

        for in_example, output in encoded_examples:
            formatted_examples.extend(
                [
                    f"Input: {in_example}",
                    f"Output: {output}",
                ]
            )

        formatted_examples.append(f"Input: {text}\nOutput:")
        input_output_block = "\n".join(formatted_examples)
        return f"{instruction_segment}\n\n{input_output_block}"

    def to_messages(self, text: str) -> List[BaseMessage]:
        """Format the template to chat messages."""
        instruction_segment = self.format_instruction_segment(self.node)

        messages: List[BaseMessage] = [SystemMessage(content=instruction_segment)]
        encoded_examples = self.generate_encoded_examples(self.node)

        for example_input, example_output in encoded_examples:
            messages.extend(
                [
                    HumanMessage(content=example_input),
                    AIMessage(content=example_output),
                ]
            )

        messages.append(HumanMessage(content=text))
        return messages

    def generate_encoded_examples(self, node: Object) -> List[Tuple[str, str]]:
        """Generate encoded examples."""
        examples = generate_examples(node)
        return encode_examples(
            examples, self.encoder, input_formatter=self.input_formatter
        )

    def format_instruction_segment(self, node: Object) -> str:
        """Generate the instruction segment of the extraction."""
        type_description = self.type_descriptor.describe(node)
        format_instructions = self.encoder.get_instruction_segment()
        input_variables = self.instruction_template.input_variables

        formatting_kwargs = {}

        if "type_description" in input_variables:
            formatting_kwargs["type_description"] = type_description

        if "format_instructions" in input_variables:
            formatting_kwargs["format_instructions"] = format_instructions

        return self.instruction_template.format(**formatting_kwargs)


# PUBLIC API


def create_langchain_prompt(
    schema: Object,
    encoder: Encoder,
    type_descriptor: TypeDescriptor,
    *,
    validator: Optional[Validator] = None,
    input_formatter: InputFormatter = None,
    instruction_template: Optional[PromptTemplate] = None,
) -> ExtractionPromptTemplate:
    """Create a langchain style prompt with specified encoder."""
    return ExtractionPromptTemplate(
        input_variables=["text"],
        output_parser=KorParser(encoder=encoder, validator=validator, schema_=schema),
        encoder=encoder,
        node=schema,
        input_formatter=input_formatter,
        type_descriptor=type_descriptor,
        instruction_template=instruction_template or DEFAULT_INSTRUCTION_TEMPLATE,
    )
