"""Code to dynamically generate appropriate LLM prompts."""

from kor.elements import Form

# PUBLIC API


def traverse_form(form: Form, depth=0):
    descriptions = []
    descriptions.append((depth, form.id, "Form", form.description))
    depth += 1
    for element in form.elements:
        if isinstance(element, Form):
            descriptions.extend(traverse_form(element, depth + 1))
        else:
            descriptions.append(
                (depth, element.id, element.finalized_type_name, element.description)
            )
    return descriptions


def generate_prompt_for_form(user_input: str, form: Form) -> str:
    """Generate a prompt for a form."""
    inputs_description_block = []
    examples = []
    for element in form.elements:
        inputs_description_block.append(f"* {element.input_full_description}")

        for example_input, example_output in element.llm_examples:
            examples.extend(
                [
                    f"Input: {example_input}",
                    f"Output: <{form.id}>{example_output}</{form.id}>",
                ]
            )

    inputs_description_block = "\n".join(inputs_description_block)
    examples_block = "\n".join(examples).strip()

    return (
        f"You are helping a user fill out a form. The user will type information and your goal "
        f"will be to parse the user's input.\n"
        f'The description of the form is: "{form.description}"'
        "Below is a list of the components showing the component ID, its type and "
        "a short description of it.\n\n"
        f"{inputs_description_block}\n\n"
        "Your task is to parse the user input and determine to what values the user is attempting "
        "to set each component of the form.\n"
        "When the type of the input is a Selection, only output one of the options specified in the square brackets "
        "as arguments to the Selection type of this input. "
        "Please enclose the extracted information in HTML style tags with the tag name "
        "corresponding to the corresponding component ID. Use angle style brackets for the "
        "tags ('>' and '<'). "
        "Only output tags when you're confident about the information that was extracted "
        "from the user's query. If you can extract several pieces of relevant information "
        'from the query include use a comma to separate the tags. If "Multiple" is part '
        "of the component's type, then please repeat the same tag multiple times once for "
        'each relevant extraction. If the type does not contain "Multiple" do not include it '
        "more than once."
        "\n\n"
        f"{examples_block}\n"
        f"Input: {user_input}\n"
        "Output: "
    )


def generate_chat_prompt_for_form(user_input: str, form: Form) -> list[dict]:
    """Generate a prompt for a form."""
    user_assistant_messages = []

    descriptions = traverse_form(form)

    form_description_block = "\n".join(
        [
            "{space}* <{id}>: {type} ({description})".format(
                space="  " * depth, id=id, type=type, description=description
            )
            for depth, id, type, description in descriptions
        ]
    )
    for element in form.elements:
        for example_input, example_output in element.llm_examples:
            user_assistant_messages.extend(
                [
                    {"role": "user", "content": example_input},
                    {
                        "role": "assistant",
                        "content": f"<{form.id}>{example_output}</{form.id}>",
                    },
                ]
            )

    user_assistant_messages.append({"role": "user", "content": user_input})

    # inputs_description_block = "\n".join(inputs_description_block)

    system_message = {
        "role": "system",
        # "content": "parse some text",
        # "content":
        #     f"You are helping a user fill out a form. The user will type information and your goal "
        # f"will be to parse the user's input.\n"
        # "content": f'The description of the form is: "{form.description}"'
        # "Below is a list of the components showing the component ID, its type and "
        # "a short description of it.\n\n"
        # # f"{inputs_description_block}\n\n"
        # "Your task is to parse the user input and determine to what values the user is attempting "
        # "to set each component of the form.\n"
        # "content": "When the type of the input is a Selection, only output one of the options specified in the square brackets "
        # "as arguments to the Selection type of this input. "
        # "Please enclose the extracted information in HTML style tags with the tag name "
        # "corresponding to the corresponding component ID. Use angle style brackets for the "
        # "tags ('>' and '<'). "
        # "Only output tags when you're confident about the information that was extracted "
        # "from the user's query. If you can extract several pieces of relevant information "
        # 'from the query, then include all of them. If "Multiple" is part '
        # "of the component's type, please repeat the same tag multiple times once for "
        # 'each relevant extraction. If the type does not contain "Multiple" do not include it '
        # "more than once.",
        "content": (
            "Your goal is to extract structured information from the user's input that matches "
            f"the form described below. The description includes the ID, type and description of "
            f"eac component.\n\n"
            f"{form_description_block}\n\n"
            "Please enclose the extracted information in HTML style tags with the tag name "
            "corresponding to the corresponding component ID. Use angle style brackets for the "
            "tags ('>' and '<'). "
            "Only output tags when you're confident about the information that was extracted "
            "from the user's query. If you can extract several pieces of relevant information "
            'from the query, then include all of them. If "Multiple" is part '
            "of the component's type, please repeat the same tag multiple times once for "
            'each relevant extraction. If the type does not contain "Multiple" do not include it '
            "more than once."
        ),
    }
    return [system_message] + user_assistant_messages
