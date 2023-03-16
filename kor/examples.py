"""Module for code that generates examples for a given input.

At the moment, this code only has a simple implementation that concatenates all the
examples, but one may want to select or generate examples in a smarter way, or take
into account the finite size of the context window and limit the number of examples.

The code uses a default encoding of XML. This encoding should match the parser.
"""
import json
from typing import Any, Callable, List, Sequence, Tuple

from kor.nodes import (
    AbstractInput,
    AbstractVisitor,
    ExtractionInput,
    Object,
    Option,
    Selection,
    TypeVar,
)
from kor.parsers.xml import encode as xml_encoder

T = TypeVar("T")


class SimpleExampleAggregator(AbstractVisitor[List[Tuple[str, str]]]):
    """Use to visit node and all of its descendents and aggregates all examples."""

    def visit_option(self, node: "Option") -> List[Tuple[str, str]]:
        """Should not visit Options directly."""
        raise AssertionError("Should never visit an Option node.")

    @staticmethod
    def _assemble_output(node: AbstractInput, data: Any) -> Any:
        """Assemble the output data according to the type of the node."""
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
                        self._assemble_output(node, example_output),
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
                    (example_input, self._assemble_output(node, example_output))
                    for example_input, example_output in child_examples
                ]

            examples.extend(child_examples)

        return examples

    def visit_selection(self, node: "Selection") -> List[Tuple[str, str]]:
        """Selection visitor."""
        examples = []
        for option in node.options:
            for example in option.examples:
                examples.append((example, self._assemble_output(node, option.id)))

        for null_example in node.null_examples:
            examples.append((null_example, ""))
        return examples

    def visit_default(self, node: "AbstractInput") -> List[Tuple[str, str]]:
        """Default visitor implementation."""
        if not isinstance(node, ExtractionInput):
            raise AssertionError()
        examples = []

        for text, extraction in node.examples:
            value = self._assemble_output(node, extraction)
            examples.append((text, value))
        return examples

    def visit(self, node: "AbstractInput") -> List[Tuple[str, str]]:
        """Entry-point."""
        return node.accept(self)




def _encode_examples(
    examples: Sequence[Tuple[str, str]], encoding: str
) -> List[Tuple[str, str]]:
    """Encode the output using the given encoder."""
    if encoding == "none":
        return list(examples)
    elif encoding == "JSON":
        encoder: Callable[[Any], str] = json.dumps
    elif encoding == "XML":
        encoder = xml_encoder
    elif encoding == "CSV":
        raise NotImplementedError()
        # encoder =
    else:
        raise NotImplementedError(f"No support for encoding {encoding}")

    return [
        (input_example, encoder(output_example))
        for input_example, output_example in examples
    ]


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
    examples = SimpleExampleAggregator().visit(element)
    encoded_examples = _encode_examples(examples, encoding)
    return encoded_examples
