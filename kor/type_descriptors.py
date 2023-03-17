"""Code that takes a object_input and outputs a string that describes its schema.

Without fine-tuning the LLM, the quality of the response may end up depending
on details such as the schema description in the prompt.

Designing the code here to make it easier to experiment with different ways
of describing the schema.
"""
import abc
from typing import List, TypeVar

from kor.nodes import AbstractInput, AbstractVisitor, Number, Object, Selection, Text

T = TypeVar("T")

# PUBLIC API


class TypeDescriptor(AbstractVisitor[T], abc.ABC):
    """Interface for type descriptors."""

    @abc.abstractmethod
    def describe(self, node: AbstractInput) -> str:
        """Take in node and describe its type as a string."""
        raise NotImplementedError()


class BulletPointTypeGenerator(TypeDescriptor[None]):
    """Mutable visitor used to generate a bullet point style schema description."""

    def __init__(self) -> None:
        self.depth = 0
        self.code_lines: List[str] = []

    def visit_default(self, node: "AbstractInput") -> None:
        """Default action for a node."""
        space = "* " + self.depth * " "
        self.code_lines.append(
            f"{space}{node.id}: {node.__class__.__name__} # {node.description}"
        )

    def visit_object(self, node: Object) -> None:
        """Visit an object node."""
        self.visit_default(node)
        self.depth += 1
        for child in node.attributes:
            child.accept(self)
        self.depth -= 1

    def get_type_description(self) -> str:
        """Get the type."""
        return "\n".join(self.code_lines)

    def describe(self, node: AbstractInput) -> str:
        """Describe the type of the given node."""
        self.code_lines = []
        node.accept(self)
        return self.get_type_description()


class TypeScriptTypeGenerator(AbstractVisitor[None]):
    """A mutable visitor (not thread safe) that helps generate TypeScript schema."""

    def __init__(self) -> None:
        self.depth = 0
        self.code_lines: List[str] = []

    def visit_default(self, node: "AbstractInput") -> None:
        """Default action for a node."""
        space = self.depth * " "

        if isinstance(node, Selection):
            finalized_type = (
                "(" + " | ".join('"' + s.id + '"' for s in node.options) + ")"
            )
        elif isinstance(node, Text):
            finalized_type = "string"
        elif isinstance(node, Number):
            finalized_type = "number"
        else:
            raise NotImplementedError()

        if node.many:
            many_formatter = "[]"
        else:
            many_formatter = ""

        self.code_lines.append(
            f"{space}{node.id}: {finalized_type}{many_formatter} // {node.description}"
        )

    def visit_object(self, node: Object) -> None:
        """Visit an object node."""
        space = self.depth * " "

        self.code_lines.append(f"{space}{node.id}: {{ // {node.description}")

        self.depth += 1
        for child in node.attributes:
            child.accept(self)
        self.depth -= 1

        self.code_lines.append(f"{space}}}")

    def get_type_description(self) -> str:
        """Get the type."""
        return "\n".join(self.code_lines)

    def describe(self, node: "AbstractInput") -> str:
        """Describe the node type in TypeScript notation."""
        self.depth = 0
        self.code_lines = []

        if not isinstance(node, Object):
            self.depth += 1  # We'll add curly brackets below at depth 0.

        node.accept(self)

        # Add curly brackets if top level node is not an object.
        if not isinstance(node, Object):
            self.code_lines.insert(0, "{")
            self.code_lines.append("}")

        return f"```TypeScript\n\n{self.get_type_description()}```\n"
