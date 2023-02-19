from kor.interpreter import Interpreter
from kor.inputs import Selection


def test_interpreter():
    state = Selection(id="selection", description="hello", options=[])
    interpreter = Interpreter(state=state)
    # interpreter.interact()
