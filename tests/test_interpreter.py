from kor.elements import Selection, compile_option_examples, Option
from kor import elements
from kor.interpreter import create_input_tree

SAMPLE_SELECTION = Selection(
    id="select-1",
    description="select something",
    examples=[],
    options=[
        Option(
            id="1",
            description="first",
            examples=["one", "i prefer the first option"],
        ),
        Option(
            id="2",
            description="second",
            examples=["the second option"],
        ),
    ],
)


def test_compile_option_example():
    option = Option(id="option", description="description", examples=["1", "2", "3"])
    example_block = compile_option_examples(option)
    assert example_block.startswith("Input: 1\nOutput: <option>\n")


def test_generate_prompt_for_selection():
    prompt = elements._generate_prompt_for_selection("user input", SAMPLE_SELECTION)
    assert prompt.startswith("You are interacting")
    assert "1" in prompt
    assert "Input: user input\n" in prompt


def test_create_input_tree_for_option():
    """Create an input tree."""
    option = Option(id="option", description="description", examples=["1", "2", "3"])
    input_tree = create_input_tree(option)
    assert list(input_tree.id_to_input) == ["option"]


def test_generate_prompt_for_form():
    form = elements.Form(id="form", description="Form", examples=[], elements=[])
    prompt = elements._generate_prompt_for_form("hello", form)
    assert isinstance(prompt, str)
