"""Code that takes a object_input and outputs a string that describes its schema.

Without fine-tuning the LLM, the quality of the response may end up depending
on details such as the object_inputat of the schema.

As a result, creating a dedicated module to allow experimenting with different
ways of describing the schema.

REWRITE in terms of visitors.
"""
from kor.elements import Selection, TextInput, AbstractInput, ObjectInput


def _auto_type_name(element: AbstractInput) -> str:
    """Automatically assign a type name."""
    return element.__class__.__name__.removesuffix("Input").lower()


def _traverse_object_input_for_bullet_point(
    object_input: ObjectInput, depth: int = 0
) -> list[tuple[int, str, str, str]]:
    """Traverse a object_input to generate a type description of its contents."""
    descriptions = [(depth, object_input.id, "Form", object_input.description)]
    depth += 1
    for element in object_input.elements:
        if isinstance(element, ObjectInput):
            descriptions.extend(
                _traverse_object_input_for_bullet_point(element, depth + 1)
            )
        else:
            descriptions.append(
                (depth, element.id, _auto_type_name(element), element.description)
            )
    return descriptions


def _traverse_object_input_obj(
    object_input: ObjectInput, is_root: bool = False
) -> dict:
    """Traverse a object_input to generate a type description of its contents."""
    obj = {}
    for element in object_input.elements:
        if isinstance(element, ObjectInput):
            obj.update({element.id: _traverse_object_input_obj(element)})
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
        return {object_input.id: obj}
    else:
        return obj


def _stringify_obj_to_typescript(obj: dict, depth: int = 0) -> str:
    """Object re-written in type-script object_inputat."""
    delimiter = " "
    outer_space = delimiter * depth
    inner_space = delimiter * (depth + 1)
    if depth == 0:
        object_inputatted = ["type Response = {"]
    else:
        object_inputatted = [f"{outer_space}" + "{"]
    for key, value in obj.items():
        if isinstance(value, dict):
            value = _stringify_obj_to_typescript(value, depth=depth + 1)
        else:
            value = value + "[]"
        object_inputatted.append(f"{inner_space}{key}: {value};")
    object_inputatted.append(f"{outer_space}" + "}[]")
    result = "\n".join(object_inputatted)
    if depth == 0:
        result += ";"
    return result


# PUBLIC API


def generate_bullet_point_description(object_input: ObjectInput) -> str:
    """Generate type description of the object_input in a custom bullet point object_inputat."""
    bullet_points = []
    summaries = _traverse_object_input_for_bullet_point(object_input, depth=0)
    for depth, uid, type_name, description in summaries:
        space = " " * depth
        bullet_points.append(f"{space}* {uid}: {type_name} # {description}")
    return "\n".join(bullet_points)  # Combine into a single block.


def generate_typescript_description(extraction_input: ObjectInput) -> str:
    """Generate a description of the object_input type in TypeScript syntax."""
    obj = _traverse_object_input_obj(extraction_input, is_root=True)
    type_script = _stringify_obj_to_typescript(obj)
    return f"```TypeScript\n{type_script}\n```\n"
