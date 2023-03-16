"""Module for code that generates examples for a given input.

At the moment, this code only has a simple implementation that concatenates all the
examples, but one may want to select or generate examples in a smarter way, or take
into account the finite size of the context window and limit the number of examples.

The code uses a default encoding of XML. This encoding should match the parser.
"""
import json
from typing import Any, List, Tuple, Union

from kor.nodes import (
    AbstractInput,
    AbstractVisitor,
    ExtractionInput,
    Object,
    Option,
    Selection,
    TypeVar,
)
from kor.xml_encoder import encode_as_xml

LiteralType = Union[str, int, float]

T = TypeVar("T")


class SimpleExampleGenerator(AbstractVisitor[List[Tuple[str, str]]]):
    def __init__(self, encoding: str):
        """Initialize the simple example generator."""
        self.encoding = encoding

    def visit_option(self, node: "Option") -> List[Tuple[str, str]]:
        """Should not visit Options directly."""
        raise AssertionError("Should never visit an Option node.")

    def _assemble_example(self, node: AbstractInput, data: Any) -> Any:
        """Apply an encoder."""
        if not data:
            return {}
        if node.multiple and not isinstance(data, (tuple, list)):
            data = [data]
        return {node.id: data}

    def visit_object(self, node: "Object") -> List[Tuple[str, str]]:
        """Implementation of an object visitor."""
        examples = []
        if node.examples:
            if node.group_as_object:
                object_examples = [
                    # Looks like false positive from mypy
                    # Can investigate how to simplify at a later point.
                    (
                        example_input,
                        self._assemble_example(node, example_output),  # type: ignore[arg-type]
                    )
                    for example_input, example_output in node.examples
                ]
                examples.extend(object_examples)
            else:
                raise NotImplementedError("Not implemented yet")

        # Collect examples from children
        for child in node.attributes:
            child_examples = child.accept(self)
            if node.group_as_object:  # Take care of namespaces
                child_examples = [
                    (example_input, self._assemble_example(node, example_output))
                    for example_input, example_output in child_examples
                ]

            examples.extend(child_examples)

        return examples

    def visit_selection(self, node: "Selection") -> List[Tuple[str, str]]:
        """Selection visitor."""
        examples = []
        for option in node.options:
            for example in option.examples:
                examples.append((example, self._assemble_example(node, option.id)))

        for null_example in node.null_examples:
            examples.append((null_example, ""))
        return examples

    def visit_default(self, node: "AbstractInput") -> List[Tuple[str, str]]:
        """Default visitor implementation."""
        if not isinstance(node, ExtractionInput):
            raise AssertionError()
        examples = []

        for text, extraction in node.examples:
            value = self._assemble_example(node, extraction)
            examples.append((text, value))
        return examples

    def visit(self, node: "AbstractInput") -> List[Tuple[str, str]]:
        """Entry-point."""
        examples = node.accept(self)
        if self.encoding == "JSON":
            return [
                (input_example, json.dumps(output_example))
                for input_example, output_example in examples
            ]
        elif self.encoding == "XML":
            return [
                (input_example, encode_as_xml(output_example))
                for input_example, output_example in examples
            ]

        return examples


# PUBLIC API


def generate_examples(
    element: AbstractInput, encoding: str = "XML"
) -> List[Tuple[str, str]]:
    """Generate examples for a given element.

    A rudimentary implementation that simply concatenates all available examples
    from the components across the entire element tree.

    Does not provide a way to impose constraints (e.g., select a subset of examples
    to meet a constraint on the overall number of tokens.)

    Args:
        element: AbstractInput
        encoding: Reserved parameter, refers to the encoding of the output, it's unclear
                  whether or how different encodings affect the ability of LLMs to match
                  a given schema


    Returns:
        list of 2-tuples containing input, output pairs
    """
    return SimpleExampleGenerator(encoding=encoding).visit(element)
