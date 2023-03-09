"""Module for code that generates examples for a given input.

At the moment, this code only has a simple implementation that concatenates all the
examples, but one may want to select or generate examples in a smarter way, or take
into account the finite size of the context window and limit the number of examples.

The code uses a default encoding of XML. This encoding should match the parser.
"""
from typing import List, Sequence, Any, Union

from kor.elements import (
    FlatForm,
    Selection,
    ExtractionInput,
    AbstractInput,
    ObjectInput,
)

LITERAL_TYPE = Union[str, int, float]


def _write_literal(tag_name: str, value: LITERAL_TYPE) -> str:
    """Write literal."""
    return f"<{tag_name}>{value}</{tag_name}>"


def _write_list(tag_name: str, values: Sequence[LITERAL_TYPE]) -> str:
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
    tag_name: str, data: LITERAL_TYPE | Sequence[LITERAL_TYPE] | dict[str, Any]
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


# PUBLIC API


def _generate_selection_examples(selection: Selection) -> list[tuple[str, str]]:
    """Generate examples for a given selection input."""
    formatted_examples = []
    for option in selection.options:
        for example in option.examples:
            formatted_examples.append((example, _write_tag(selection.id, option.id)))

    for null_example in selection.null_examples:
        formatted_examples.append((null_example, ""))

    return formatted_examples


def _generate_extraction_input_examples(
    extraction_input: ExtractionInput,
) -> list[tuple[str, str]]:
    """List of 2-tuples of input, output.

    Does not include the `Input: ` or `Output: ` prefix
    """
    formatted_examples = []
    for text, extraction in extraction_input.examples:
        if isinstance(extraction, str) and not extraction.strip():
            value = ""
        else:
            value = _write_tag(extraction_input.id, extraction)
        formatted_examples.append((text, value))
    return formatted_examples


def _generate_examples_object(obj: Union[FlatForm]) -> List[tuple[str, str]]:
    """Generate examples form."""
    examples = []
    for element in obj.elements:
        element_examples = generate_examples(element)
        # If the form is to be interpreted as a coherent object, then
        # we do a trick and wrap all the outputs in the form ID.
        if (
            isinstance(obj, FlatForm) and obj.as_object
        ):  # Wrap all examples in a parent tag
            element_examples = [
                (example_input, _write_tag(obj.id, example_output))
                for example_input, example_output in element_examples
            ]

        examples.extend(element_examples)

    object_examples = obj.examples

    if isinstance(obj, ObjectInput):
        object_examples = [
            (example_input, _write_tag(obj.id, example_output))
            for example_input, example_output in object_examples
        ]
    else:
        if object_examples:
            raise NotImplementedError(
                f"No support form examples if form is not an object."
            )

    examples.extend(object_examples)

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
    # Dispatch based on element type.
    if isinstance(element, (ObjectInput, FlatForm)):
        return _generate_examples_object(element)
    elif isinstance(element, Selection):
        return _generate_selection_examples(element)
    elif isinstance(element, ExtractionInput):  # Catch all
        return _generate_extraction_input_examples(element)
    else:
        raise NotImplementedError(f"No support for {type(element)}")
