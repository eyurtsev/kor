"""Code that takes a form and outputs a string that describes its schema.

Without fine-tuning the LLM, the quality of the response may end up depending
on details such as the format of the schema.

As a result, creating a dedicated module to allow experimenting with different
ways of describing the schema.
"""
from kor.elements import FlatForm, Selection, TextInput, AbstractInput


def _auto_type_name(element: AbstractInput) -> str:
    """Automatically assign a type name."""
    return element.__class__.__name__.removesuffix("Input").lower()


def _traverse_form_for_bullet_point(
    form: FlatForm, depth: int = 0
) -> list[tuple[int, str, str, str]]:
    """Traverse a form to generate a type description of its contents."""
    descriptions = [(depth, form.id, "Form", form.description)]
    depth += 1
    for element in form.elements:
        if isinstance(element, FlatForm):
            descriptions.extend(_traverse_form_for_bullet_point(element, depth + 1))
        else:
            descriptions.append(
                (depth, element.id, _auto_type_name(element), element.description)
            )
    return descriptions


def _traverse_form_obj(form: FlatForm, is_root: bool = False) -> dict:
    """Traverse a form to generate a type description of its contents."""
    obj = {}
    for element in form.elements:
        if isinstance(element, FlatForm):
            obj.update({element.id: _traverse_form_obj(element)})
        else:
            if isinstance(element, Selection):
                finalized_type = (
                    "(" + " | ".join('"' + s.id + '"' for s in element.options) + ")"
                )
            elif isinstance(element, TextInput):
                finalized_type = "string"
            else:
                finalized_type = _auto_type_name(element)
            obj.update({element.id: finalized_type})

    if is_root:
        return {form.id: obj}
    else:
        return obj


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


def generate_bullet_point_description(form: FlatForm) -> str:
    """Generate type description of the form in a custom bullet point format."""
    bullet_points = []
    summaries = _traverse_form_for_bullet_point(form, depth=0)
    for depth, uid, type_name, description in summaries:
        space = " " * depth
        bullet_points.append(f"{space}* {uid}: {type_name} # {description}")
    return "\n".join(bullet_points)  # Combine into a single block.


def generate_typescript_description(form: FlatForm) -> str:
    """Generate a description of the form type in TypeScript syntax."""
    obj = _traverse_form_obj(form, is_root=True)
    type_script = _stringify_obj_to_typescript(obj)
    return f"```TypeScript\n{type_script}\n```\n"
