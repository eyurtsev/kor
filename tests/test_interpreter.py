import kor.experimental.other_prompts
import kor.prompts
from kor.elements import Selection, Option
from kor.experimental.other_prompts import _compile_option_examples
from kor import elements
from kor.experimental.interpreter import create_input_tree

SAMPLE_SELECTION = Selection(
    id="select",
    description="select something",
    options=[
        Option(
            id="o1",
            description="first",
            examples=["one", "i prefer the first option"],
        ),
        Option(
            id="o2",
            description="second",
            examples=["the second option"],
        ),
    ],
)


def test_compile_option_example():
    option = Option(id="option", description="description", examples=["1", "2", "3"])
    example_block = _compile_option_examples("s", option)
    assert example_block.startswith("Input: 1\nOutput: <s>option</s>\n")


def test_generate_prompt_for_selection():
    prompt = kor.experimental.other_prompts._generate_prompt_for_selection(
        "user input", SAMPLE_SELECTION
    )
    assert prompt.startswith("You are interacting")
    assert "1" in prompt
    assert "Input: user input\n" in prompt


def test_create_input_tree_for_option():
    """Create an input tree."""
    option = Option(id="option", description="description", examples=["1", "2", "3"])
    input_tree = create_input_tree(option)
    assert list(input_tree.id_to_input) == ["option"]


def test_generate_prompt_for_form():
    form = elements.FlatForm(id="form", description="Form", elements=[])
    prompt = kor.prompts.generate_prompt_for_form("hello", form)
    assert isinstance(prompt, str)
