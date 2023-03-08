"""Module for code that generates examples for a given form.

At the moment, this code only has a simple implementation that concatenates all the
examples, but one may want to select or generate examples in a smarter way, or take
into account the finite size of the context window and limit the number of examples.
"""
from typing import List, Sequence, Any

from kor.elements import Form, Selection, ExtractionInput, AbstractInput


def _write_single_tag(tag_name: str, value: str) -> str:
    """Write a tag."""
    return f"<{tag_name}>{value}</{tag_name}>"


def _write_list(tag_name: str, values: Sequence[str]) -> str:
    """Write list."""
    return "".join(_write_tag(tag_name, value) for value in values)


def _write_complex_tag(tag_name: str, data: dict[str, str]) -> str:
    """Write a complex tag."""
    s_data = "".join(
        [
            _write_tag(key, value)
            for key, value in sorted(data.items(), key=lambda item: item[0])
        ]
    )
    return _write_tag(tag_name, s_data)


def _write_tag(tag_name: str, data: str | Sequence[str] | dict[str, Any]) -> str:
    """Write a tag."""
    if isinstance(data, (str, int, float, complex)):
        return _write_single_tag(tag_name, data)
    elif isinstance(data, list):
        return _write_list(tag_name, data)
    elif isinstance(data, dict):
        return _write_complex_tag(tag_name, data)
    else:
        raise NotImplementedError(f"No support for {tag_name}")


# PUBLIC API


def _generate_selection_examples(selection: Selection, encoding: str) -> list[tuple[str, str]]:
    """Generate examples for a given selection input."""
    formatted_examples = []
    for option in selection.options:
        for example in option.examples:
            formatted_examples.append((example, _write_tag(selection.id, option.id)))

    for null_example in selection.null_examples:
        formatted_examples.append((null_example, ""))

    return formatted_examples


def _generate_extraction_input_examples(
    extraction_input: ExtractionInput, encoding: str
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


def _generate_examples_form(form: Form, encoding: str) -> List[tuple[str, str]]:
    """Generate examples form."""
    examples = []
    for element in form.elements:
        element_examples = generate_examples(element, encoding=encoding)
        # If the form is to be interpreted as a coherent object, then
        # we do a trick and wrap all the outputs in the form ID.
        if form.as_object:  # Wrap all examples in a parent tag
            element_examples = [
                (example_input, _write_tag(form.id, example_output))
                for example_input, example_output in element_examples
            ]

        examples.extend(element_examples)

    form_examples = form.examples
    if form.as_object:
        form_examples = [
            (example_input, _write_tag(form.id, example_output))
            for example_input, example_output in form_examples
        ]
    else:
        raise NotImplementedError(f"No support form examples if form is not an object.")

    examples.extend(form_examples)

    return examples


def generate_examples(element: AbstractInput, encoding: str = 'XML') -> List[tuple[str, str]]:
    """Dispatch based on element type."""
    if isinstance(element, Form):
        return _generate_examples_form(element, encoding=encoding)
    elif isinstance(element, Selection):
        return _generate_selection_examples(element, encoding=encoding)
    elif isinstance(element, ExtractionInput):  # Catch all
        return _generate_extraction_input_examples(element, encoding=encoding)
    else:
        raise NotImplementedError(f"No support for {type(element)}")


simple_example_generator = generate_examples
