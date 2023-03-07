"""Module for code that generates examples for a given form.

At the moment, this code only has a simple implementation that concatenates all the
examples, but one may want to select or generate examples in a smarter way, or take
into account the finite size of the context window and limit the number of examples.
"""
from typing import List

from kor.elements import Form


# PUBLIC API


def simple_example_generator(form: Form) -> List[tuple[str, str]]:
    """Simple built-in example generator for a form."""
    examples = []
    for element in form.elements:
        examples.extend(element.llm_examples)
    return examples
