"""Code to dynamically generate appropriate LLM prompts."""
import abc
import dataclasses
from typing import Union, Literal, Callable, List, Tuple

from kor.elements import Form, Selection, TextInput

prompt_format = Union[Literal["openai-chat"], Literal["string"]]


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


def _form_as_typescript(form: Form) -> str:
    """Generate a description of the form type in TypeScript syntax."""
    obj = _traverse_form_obj(form)
    return _print_as_typescript_object(obj)


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


def _print_as_typescript_object(obj: dict, depth: int = 0) -> str:
    """Object re-written in type-script format."""
    delimiter = " "
    outer_space = delimiter * depth
    inner_space = delimiter * (depth + 1)
    if depth == 0:
        formatted = ["type Response =  {"]
    else:
        formatted = [f"{outer_space}" + "{"]
    for key, value in obj.items():
        if isinstance(value, dict):
            value = _print_as_typescript_object(value, depth=depth + 1)
        else:
            value = value + "[]"
        formatted.append(f"{inner_space}{key}: {value};")
    formatted.append(f"{outer_space}" + "}[]")
    result = "\n".join(formatted)
    if depth == 0:
        result += ";"
    return result


def generate_custom_type_description(form: Form) -> str:
    """Generate form."""
    inputs_description_block = []
    for element in form.elements:
        inputs_description_block.append(f"* {element.input_full_description}")
    inputs_description_block = "\n".join(inputs_description_block)
    return inputs_description_block


# INSTRUCTIONS_PROMPT = (
#     "{prefix}\n\n"
#     "{type_description}"
#     "{suffix}\n\n"
#     f"```Typescript"
#     f"{type_description}\n\n"
#     f"```"
#     "Please enclose the extracted information in HTML style tags with the tag name "
#     "corresponding to the corresponding component ID. Use angle style brackets for the "
#     "tags ('>' and '<'). "
#     "Only output tags when you're confident about the information that was extracted "
#     "from the user's query. If you can extract several pieces of relevant information "
#     'from the query, then include all of them. If "Multiple" is part '
#     "of the component's type, please repeat the same tag multiple times once for "
#     'each relevant extraction. If the type does not contain "Multiple" do not include it '
#     "more than once."
# )


def simple_example_generator(form: Form) -> List[tuple[str, str]]:
    """Simple built-in example generator for a form."""
    examples = []
    for element in form.elements:
        examples.extend(element.llm_examples)
    return examples


@dataclasses.dataclass(frozen=True, kw_only=True)
class PromptGenerator(abc.ABC):
    """Define abstract interface for a prompt."""

    @abc.abstractmethod
    def format_standard(self, user_input: str, form: Form) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def format_chat(self, user_input: str, form: Form) -> list[dict[str, str]]:
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True, kw_only=True)
class ExtractionTemplate(PromptGenerator):
    """Prompt generator for extraction purposes."""

    prefix: str
    type_descriptor: str
    suffix: str
    example_generator: Callable[
        [Form], List[Tuple[str, str]]
    ] = simple_example_generator

    def __post_init__(self) -> None:
        """Validate the template."""
        if self.prefix.endswith("\n"):
            raise ValueError("Please do not end the prefix with new lines.")

        if self.suffix.endswith("\n"):
            raise ValueError("Please do not end the suffix with new lines.")

    def generate_instruction_segment(self, form: Form):
        """Generate instructions."""
        type_description = _form_as_typescript(form)
        return f"{self.prefix}\n\n{type_description}\n\n{self.suffix}"

    def format_standard(self, user_input: str, form: Form) -> str:
        """Format the template for a `standard` LLM model."""
        instruction_segment = self.generate_instruction_segment(form)
        examples = self.example_generator(form)
        input_output_block = []

        for in_example, output in examples:
            input_output_block.extend(
                [
                    f"Input: {in_example}",
                    f"Output: {output}",
                ]
            )

        input_output_block.append(f"Input: {user_input}\nOutput:")
        input_output_block = "\n".join(input_output_block)
        return f"{instruction_segment}\n\n{input_output_block}"

    def format_chat(self, user_input: str, form: Form) -> list[dict[str, str]]:
        """Format the template for a `chat` LLM model."""
        raise NotImplementedError()
        # instruction_segment = self.generate_instruction_segment(form)


# class PromptGenerator:
#     def __init__(self) -> None:
#         """Generate."""
#         self.instructions_prompt = (
#             "Your goal is to extract structured information from the user's input that matches "
#             f"the form described below. "
#             f"When extracting information please make sure it matches the type information exactly. "
#             f"IMPORATNT: For Union types the output must EXACTLY match one of the members of the Union type. "
#             f"\n\n"
#             f"```Typescript"
#             f"{type_description}\n\n"
#             f"```"
#             "Please enclose the extracted information in HTML style tags with the tag name "
#             "corresponding to the corresponding component ID. Use angle style brackets for the "
#             "tags ('>' and '<'). "
#             "Only output tags when you're confident about the information that was extracted "
#             "from the user's query. If you can extract several pieces of relevant information "
#             'from the query, then include all of them. If "Multiple" is part '
#             "of the component's type, please repeat the same tag multiple times once for "
#             'each relevant extraction. If the type does not contain "Multiple" do not include it '
#             "more than once."
#         )
#
#     def generate_type_description(self, form: Form) -> str:
#         """Generate a description of the type."""
#         return _form_as_typescript(form)
#
#     def generate_examples(self, form: Form):
#         # Add user assistant messages
#         for element in form.elements:
#             for example_input, example_output in element.llm_examples:
#                 messages.extend(
#                     [
#                         {"role": "user", "content": example_input},
#                         {
#                             "role": "assistant",
#                             "content": f"<{form.id}>{example_output}</{form.id}>",
#                         },
#                     ]
#                 )
#             return []
#
#     def generate_prompt_for_form_chat(self, user_input: str, form: Form):
#         """Generate a prompt for the given form."""
#         # Generate prompt in chat format.
#
#         # "Your goal is to extract structured information from the user's input that matches "
#         # f"the form described below. "
#         # f"When extracting information please make sure it matches the type information exactly. "
#         # f"IMPORATNT: For Union types the output must EXACTLY match one of the members of the Union type. "
#         # f"\n\n"
#         # f"```Typescript"
#         # f"{type_description}\n\n"
#         # f"```"
#         # "Please enclose the extracted information in HTML style tags with the tag name "
#         # "corresponding to the corresponding component ID. Use angle style brackets for the "
#         # "tags ('>' and '<'). "
#         # "Only output tags when you're confident about the information that was extracted "
#         # "from the user's query. If you can extract several pieces of relevant information "
#         # 'from the query, then include all of them. If "Multiple" is part '
#         # "of the component's type, please repeat the same tag multiple times once for "
#         # 'each relevant extraction. If the type does not contain "Multiple" do not include it '
#         # "more than once."
#
#         type_description = self.generate_type_description(form)
#         system_message = {
#             "role": "system",
#             "content": (),
#         }
#
#         messages = [system_message]
#         messages.extend(self.generate_examples(form))
#         messages.append({"role": "user", "content": user_input})
#         return messages
#
#     # def generate_prompt_for_form_old
#
#
# # PUBLIC API
#
#
# def generate_prompt_for_form(user_input: str, form: Form) -> str:
#     """Generate a prompt for a form."""
#     examples = []
#     for element in form.elements:
#         for example_input, example_output in element.llm_examples:
#             examples.extend(
#                 [
#                     f"Input: {example_input}",
#                     f"Output: <{form.id}>{example_output}</{form.id}>",
#                 ]
#             )
#
#     examples_block = "\n".join(examples).strip()
#
#     form_description_block = _form_as_typescript(form)
#     return (
#         "Your goal is to extract structured information from the user's input that matches "
#         f"the form described below. "
#         f"When extracting information please make sure it matches the type information exactly. "
#         f"IMPORATNT: For Union types the output must EXACTLY match one of the members of the Union type. "
#         f"\n\n"
#         f"```Typescript\n"
#         f"{form_description_block}\n\n"
#         f"```\n\n"
#         "Your task is to parse the user input and determine to what values the user is attempting "
#         "to set each component of the form.\n"
#         "When the type of the input is a Selection, only output one of the options "
#         "specified in the square brackets "
#         "as arguments to the Selection type of this input. "
#         "Please enclose the extracted information in HTML style tags with the tag name "
#         "corresponding to the corresponding component ID. Use angle style brackets for the "
#         "tags ('>' and '<'). "
#         "Only output tags when you're confident about the information that was extracted "
#         "from the user's query. If you can extract several pieces of relevant information "
#         'from the query include use a comma to separate the tags. If "Multiple" is part '
#         "of the component's type, then please repeat the same tag multiple times once for "
#         'each relevant extraction. If the type does not contain "Multiple" do not include it '
#         "more than once."
#         "\n\n"
#         f"{examples_block}\n"
#         f"Input: {user_input}\n"
#         "Output: "
#     )
#

#
# def generate_chat_prompt_for_form(user_input: str, form: Form) -> list[dict]:
#     """Generate a prompt for a form."""
#     # Generate system message which contains instructions.
#     # descriptions = _traverse_form(form)
#     # form_description_block = "\n".join(
#     #     [
#     #         "{space}* <{id}>: {type} ({description})".format(
#     #             space="  " * depth, id=id, type=type, description=description
#     #         )
#     #         for depth, id, type, description in descriptions
#     #     ]
#     # )
#     form_description_block = _form_as_typescript(form)
#     system_message = {
#         "role": "system",
#         "content": (
#             "Your goal is to extract structured information from the user's input that matches "
#             f"the form described below. "
#             f"When extracting information please make sure it matches the type information exactly. "
#             f"IMPORATNT: For Union types the output must EXACTLY match one of the members of the Union type. "
#             f"\n\n"
#             f"```Typescript"
#             f"{form_description_block}\n\n"
#             f"```"
#             "Please enclose the extracted information in HTML style tags with the tag name "
#             "corresponding to the corresponding component ID. Use angle style brackets for the "
#             "tags ('>' and '<'). "
#             "Only output tags when you're confident about the information that was extracted "
#             "from the user's query. If you can extract several pieces of relevant information "
#             'from the query, then include all of them. If "Multiple" is part '
#             "of the component's type, please repeat the same tag multiple times once for "
#             'each relevant extraction. If the type does not contain "Multiple" do not include it '
#             "more than once."
#         ),
#     }
#
#     messages = [system_message]
#
#     # Add user assistant messages
#     for element in form.elements:
#         for example_input, example_output in element.llm_examples:
#             messages.extend(
#                 [
#                     {"role": "user", "content": example_input},
#                     {
#                         "role": "assistant",
#                         "content": f"<{form.id}>{example_output}</{form.id}>",
#                     },
#                 ]
#             )
#
#     messages.append({"role": "user", "content": user_input})
#     return messages
