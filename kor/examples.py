"""Module for code that generates examples for a given input.

At the moment, this code only has a simple implementation that concatenates all the
examples, but one may want to select or generate examples in a smarter way, or take
into account the finite size of the context window and limit the number of examples.

The code uses a default encoding of XML. This encoding should match the parser.
"""
import json
from typing import Any, Dict, List, Mapping, Sequence, Tuple, Union

from kor.nodes import (
    AbstractInput,
    AbstractVisitor,
    ExtractionInput,
    Object,
    Option,
    Selection,
    TypeVar,
)

LiteralType = Union[str, int, float]


def _write_literal(tag_name: str, value: LiteralType) -> str:
    """Write literal."""
    return f"<{tag_name}>{value}</{tag_name}>"


def _write_list(tag_name: str, values: Sequence[LiteralType]) -> str:
    """Write list."""
    return "".join(_write_tag(tag_name, value) for value in values)


def _write_dict(tag_name: str, data: Mapping[str, Any]) -> str:
    """Write a dict."""
    s_data = "".join(
        [
            _write_tag(key, value)
            for key, value in sorted(data.items(), key=lambda item: item[0])
        ]
    )
    return _write_tag(tag_name, s_data)


def _write_tag(
    tag_name: str, data: Union[LiteralType, Sequence[LiteralType], Mapping[str, Any]]
) -> str:
    """Write a tag."""
    # Dispatch based on type.
    if isinstance(data, (str, int, float)):
        return _write_literal(tag_name, data)
    elif isinstance(data, list):
        return _write_list(tag_name, data)
    elif isinstance(data, dict):
        return _write_dict(tag_name, data)
    else:
        raise NotImplementedError(f"No support for {tag_name}")


T = TypeVar("T")


class SimpleExampleGenerator(AbstractVisitor[List[Tuple[str, str]]]):
    def __init__(self, encoding: str):
        """Initialize the simple example generator."""
        self.encoding = encoding

    def visit_option(self, node: "Option") -> List[Tuple[str, str]]:
        """Should not visit Options directly."""
        raise AssertionError("Should never visit an Option node.")

    def _xml_encoder(self, node: AbstractInput, data: Any) -> str:
        """Encode the data into XML format."""
        if isinstance(data, str) and not data.strip():
            return _write_tag(node.id, "")
        return _write_tag(node.id, data)

    def _plain_encoder(self, node: AbstractInput, data: Any) -> Dict[str, Any]:
        """Encode maintaining the data as a plain python object."""
        if not data:
            return {}
        if node.multiple and not isinstance(data, (tuple, list)):
            data = [data]
        return {node.id: data}

    def _encode(self, node: AbstractInput, data: Any) -> Any:
        """Apply an encoder."""
        if self.encoding == "XML":
            return self._xml_encoder(node, data)
        elif self.encoding in {"plain", "JSON"}:
            return self._plain_encoder(node, data)
        else:
            raise NotImplementedError()

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
                        self._encode(node, example_output),  # type: ignore[arg-type]
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
                    (example_input, self._encode(node, example_output))
                    for example_input, example_output in child_examples
                ]

            examples.extend(child_examples)

        return examples

    def visit_selection(self, node: "Selection") -> List[Tuple[str, str]]:
        """Selection visitor."""
        examples = []
        for option in node.options:
            for example in option.examples:
                examples.append((example, self._encode(node, option.id)))

        for null_example in node.null_examples:
            examples.append((null_example, ""))
        return examples

    def visit_default(self, node: "AbstractInput") -> List[Tuple[str, str]]:
        """Default visitor implementation."""
        if not isinstance(node, ExtractionInput):
            raise AssertionError()
        examples = []

        for text, extraction in node.examples:
            value = self._encode(node, extraction)
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
