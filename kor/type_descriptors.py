"""Code that takes a form and outputs a string that describes its schema.

Without fine-tuning the LLM, the quality of the response may end up depending
on details such as the format of the schema.

As a result, creating a dedicated module to allow experimenting with different
ways of describing the schema.
"""
from kor.elements import Form, Selection, TextInput


def _traverse_form(form: Form, depth: int = 0) -> list[tuple[int, str, str, str]]:
    """Traverse a form to generate a type description of its contents."""
    descriptions = [(depth, form.id, "Form", form.description)]
    depth += 1
    for element in form.elements:
        if isinstance(element, Form):
            descriptions.extend(_traverse_form(element, depth + 1))
        else:
            descriptions.append(
                (depth, element.id, element.type_name, element.description)
            )
    return descriptions


def _traverse_form_obj(form: Form) -> dict:
    """Traverse a form to generate a type description of its contents."""
    obj = {}
    for element in form.elements:
        if isinstance(element, Form):
            obj.update({element.id: _traverse_form_obj(element)})
        else:
            if isinstance(element, Selection):
                finalized_type = (
                    "(" + " | ".join('"' + s.id + '"' for s in element.options) + ")"
                )
            elif isinstance(element, TextInput):
                finalized_type = "string"
            else:
                finalized_type = element.type_name.lower()
            obj.update({element.id: finalized_type})
    return {form.id: obj}


def _stringify_obj_to_typescript(obj: dict, depth: int = 0) -> str:
    """Object re-written in type-script format."""
    delimiter = " "
    outer_space = delimiter * depth
    inner_space = delimiter * (depth + 1)
    if depth == 0:
        formatted = ["type Response = {"]
    else:
        formatted = [f"{outer_space}" + "{"]
    for key, value in obj.items():
        if isinstance(value, dict):
            value = _stringify_obj_to_typescript(value, depth=depth + 1)
        else:
            value = value + "[]"
        formatted.append(f"{inner_space}{key}: {value};")
    formatted.append(f"{outer_space}" + "}[]")
    result = "\n".join(formatted)
    if depth == 0:
        result += ";"
    return result


# PUBLIC API


def generate_bullet_point_description(form: Form) -> str:
    """Generate type description of the form in a custom bullet point format."""
    bullet_points = []
    for element in form.elements:
        bull_point_description = (
            f"* {element.id}: {element.type_name} # {element.description}"
        )
        bullet_points.append(bull_point_description)
    return "\n".join(bullet_points)  # Combine into a single block.


def generate_typescript_description(form: Form) -> str:
    """Generate a description of the form type in TypeScript syntax."""
    obj = _traverse_form_obj(form)
    return _stringify_obj_to_typescript(obj)
