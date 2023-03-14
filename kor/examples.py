"""Module for code that generates examples for a given input.

At the moment, this code only has a simple implementation that concatenates all the
examples, but one may want to select or generate examples in a smarter way, or take
into account the finite size of the context window and limit the number of examples.

The code uses a default encoding of XML. This encoding should match the parser.
"""
from typing import Any, List, Sequence, Tuple, Union

from kor.nodes import (
    AbstractInput,
    AbstractVisitor,
    ExtractionInput,
    Object,
    Option,
    Selection,
)

LiteralType = Union[str, int, float]


def _write_literal(tag_name: str, value: LiteralType) -> str:
    """Write literal."""
    return f"<{tag_name}>{value}</{tag_name}>"


def _write_list(tag_name: str, values: Sequence[LiteralType]) -> str:
    """Write list."""
    return "".join(_write_tag(tag_name, value) for value in values)


def _write_dict(tag_name: str, data: dict[str, Any]) -> str:
    """Write a dict."""
    s_data = "".join(
        [
            _write_tag(key, value)
            for key, value in sorted(data.items(), key=lambda item: item[0])
        ]
    )
    return _write_tag(tag_name, s_data)


def _write_tag(
    tag_name: str, data: Union[LiteralType, Sequence[LiteralType], dict[str, Any]]
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


class SimpleExampleGenerator(AbstractVisitor[List[Tuple[str, str]]]):
    def visit_option(self, node: "Option") -> List[Tuple[str, str]]:
        raise AssertionError("Should never visit an Option node.")

    def visit_object(self, node: "Object") -> List[Tuple[str, str]]:
        if node.group_as_object and node.examples:
            object_examples = [
                # Looks like false positive from mypy
                # Can investigate how to simplify at a later point.
                (
                    example_input,
                    _write_tag(node.id, example_output),  # type: ignore[arg-type]
                )
                for example_input, example_output in node.examples
            ]
        else:
            raise NotImplementedError("Not implemented yet")

        examples = object_examples

        # Collect examples from children
        for child in node.attributes:
            child_examples = child.accept(self)
            if node.group_as_object:  # Take care of namespaces
                child_examples = [
                    (example_input, _write_tag(node.id, example_output))
                    for example_input, example_output in child_examples
                ]

            examples.extend(child_examples)

        return examples

    def visit_selection(self, node: "Selection") -> List[Tuple[str, str]]:
        examples = []
        for option in node.options:
            for example in option.examples:
                examples.append((example, _write_tag(node.id, option.id)))

        for null_example in node.null_examples:
            examples.append((null_example, ""))
        return examples

    def visit_default(self, node: "AbstractInput") -> List[Tuple[str, str]]:
        """Default visitor implementation."""
        if not isinstance(node, ExtractionInput):
            raise AssertionError()
        examples = []

        for text, extraction in node.examples:
            if isinstance(extraction, str) and not extraction.strip():
                value = ""
            else:
                value = _write_tag(node.id, extraction)
            examples.append((text, value))
        return examples


# PUBLIC API


def generate_examples(
    element: AbstractInput, encoding: str = "XML"
) -> List[tuple[str, str]]:
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
    if encoding != "XML":
        raise NotImplementedError("Only XML encoding is supported right now.")

    example_generator = SimpleExampleGenerator()
    examples = element.accept(example_generator)
    return examples
