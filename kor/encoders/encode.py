from typing import List, Sequence, Tuple

from .typedefs import Encoder

# PUBLIC API


def encode_examples(
    examples: Sequence[Tuple[str, str]], encoder: Encoder
) -> List[Tuple[str, str]]:
    """Encode the output using the given encoder."""
    return [
        (input_example, encoder.encode(output_example))
        for input_example, output_example in examples
    ]
