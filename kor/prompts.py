"""Code to dynamically generate appropriate LLM prompts."""
from __future__ import annotations

from typing import Any, List, Optional, Tuple

from langchain import BasePromptTemplate
from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    PromptValue,
    SystemMessage,
)
from pydantic import Extra

from kor.encoders import Encoder
from kor.encoders.encode import encode_examples
from kor.encoders.parser import KorParser
from kor.examples import generate_examples
from kor.nodes import AbstractSchemaNode
from kor.type_descriptors import TypeDescriptor

from .validators import Validator


class ExtractionPromptValue(PromptValue):
    """Integration with langchain prompt format."""

    text: str
    encoder: Encoder
    node: AbstractSchemaNode
    type_descriptor: TypeDescriptor
    prefix: str = (
        "Your goal is to extract structured information from the user's input that"
        " matches the form described below. When extracting information please make"
        " sure it matches the type information exactly. Do not add any attributes that"
        " do not appear in the schema shown below."
    )

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def to_string(self) -> str:
        """Format the template to a string."""
        instruction_segment = self.generate_instruction_segment(self.node)
        encoded_examples = self.generate_encoded_examples(self.node)
        formatted_examples: List[str] = []

        for in_example, output in encoded_examples:
            formatted_examples.extend(
                [
                    f"Input: {in_example}",
                    f"Output: {output}",
                ]
            )

        formatted_examples.append(f"Input: {self.text}\nOutput:")
        input_output_block = "\n".join(formatted_examples)
        return f"{instruction_segment}\n\n{input_output_block}"

    def to_messages(self) -> List[BaseMessage]:
        """Format the template to chat messages."""
        instruction_segment = self.generate_instruction_segment(self.node)

        messages: List[BaseMessage] = [SystemMessage(content=instruction_segment)]
        encoded_examples = self.generate_encoded_examples(self.node)

        for example_input, example_output in encoded_examples:
            messages.extend(
                [
                    HumanMessage(content=example_input),
                    AIMessage(content=example_output),
                ]
            )

        messages.append(HumanMessage(content=self.text))
        return messages

    def generate_encoded_examples(
        self, node: AbstractSchemaNode
    ) -> List[Tuple[str, str]]:
        """Generate encoded examples."""
        examples = generate_examples(node)
        return encode_examples(examples, self.encoder)

    def generate_instruction_segment(self, node: AbstractSchemaNode) -> str:
        """Generate the instruction segment of the extraction."""
        type_description = self.type_descriptor.describe(node)
        instruction_segment = self.encoder.get_instruction_segment()
        return f"{self.prefix}\n\n{type_description}\n\n{instruction_segment}"


class ExtractionPromptTemplate(BasePromptTemplate):
    """Extraction prompt template."""

    encoder: Encoder
    node: AbstractSchemaNode
    type_descriptor: TypeDescriptor

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def format_prompt(  # type: ignore[override]
        self, text: str, **kwargs: Any
    ) -> PromptValue:
        """Format the prompt."""
        return ExtractionPromptValue(
            text=text,
            encoder=self.encoder,
            node=self.node,
            type_descriptor=self.type_descriptor,
        )

    def format(self, **kwargs: Any) -> str:
        """Implementation of deprecated format method."""
        raise NotImplementedError()

    @property
    def _prompt_type(self) -> str:
        """Prompt type."""
        return "ExtractionPromptTemplate"


# PUBLIC API


def create_langchain_prompt(
    schema: AbstractSchemaNode,
    encoder: Encoder,
    type_descriptor: TypeDescriptor,
    validator: Optional[Validator] = None,
) -> ExtractionPromptTemplate:
    """Create a langchain style prompt with specified encoder."""
    return ExtractionPromptTemplate(
        input_variables=["text"],
        output_parser=KorParser(encoder=encoder, validator=validator, schema_=schema),
        encoder=encoder,
        node=schema,
        type_descriptor=type_descriptor,
    )
