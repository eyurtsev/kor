"""Code that takes an Object schema and outputs a string that describes its schema.

Without fine-tuning the LLM, the quality of the response may end up depending
on details such as the schema description in the prompt.

Users can implement their own type descriptors or customize an existing one
using inheritance and over-loading and provide the type-descriptors to
the create_extraction_chain function.
"""
import abc
from typing import Any, Iterable, List, TypeVar, Union

from kor.nodes import (
    AbstractSchemaNode,
    AbstractVisitor,
    Bool,
    Number,
    Object,
    Selection,
    Text,
)

T = TypeVar("T")

# PUBLIC API


class TypeDescriptor(AbstractVisitor[T], abc.ABC):
    """Abstract interface for a type-descriptor.

    A type-descriptor is responsible for taking in a schema and outputting its type
    as a string. The description is used to help the LLM generate structured output.

    A type-descriptor is a visitor that can be used to traverse the schema recursively.
    """

    @abc.abstractmethod
    def describe(self, node: Object) -> str:
        """Take in node and describe its type as a string."""
        raise NotImplementedError()


class BulletPointDescriptor(TypeDescriptor[Iterable[str]]):
    """Generate a bullet point style schema description."""

    def visit_default(self, node: "AbstractSchemaNode", **kwargs: Any) -> List[str]:
        """Default action for a node."""
        depth = kwargs["depth"]
        space = "* " + depth * " "
        return [f"{space}{node.id}: {node.__class__.__name__} # {node.description}"]

    def visit_object(self, node: Object, **kwargs: Any) -> List[str]:
        """Visit an object node."""
        depth = kwargs["depth"]
        code_lines = self.visit_default(node, depth=depth)
        for child in node.attributes:
            code_lines.extend(child.accept(self, depth=depth + 1))
        return code_lines

    def describe(self, node: Object) -> str:
        """Describe the type of the given node."""
        code_lines = node.accept(self, depth=0)
        return "\n".join(code_lines)


class TypeScriptDescriptor(TypeDescriptor[Iterable[str]]):
    """Generate a typescript style schema description."""

    def visit_default(self, node: "AbstractSchemaNode", **kwargs: Any) -> List[str]:
        """Default action for a node."""
        depth = kwargs["depth"]
        space = depth * " "

        if isinstance(node, Selection):
            finalized_type = " | ".join('"' + s.id + '"' for s in node.options)
        elif isinstance(node, Text):
            finalized_type = "string"
        elif isinstance(node, Number):
            finalized_type = "number"
        elif isinstance(node, Bool):
            finalized_type = "boolean"
        else:
            raise NotImplementedError()

        if node.many:
            finalized_type = "Array<" + finalized_type + ">"

        return [f"{space}{node.id}: {finalized_type} // {node.description}"]

    def visit_object(self, node: Object, **kwargs: Any) -> List[str]:
        """Visit an object node."""
        depth = kwargs["depth"]
        space = depth * " "

        if node.many:
            many_formatter = "Array<"
        else:
            many_formatter = ""

        code_lines = [f"{space}{node.id}: {many_formatter}{{ // {node.description}"]

        for child in node.attributes:
            code_lines.extend(child.accept(self, depth=depth + 1))

        if node.many:
            many_formatter = ">"
        else:
            many_formatter = ""

        code_lines.append(f"{space}}}{many_formatter}")
        return code_lines

    def describe(self, node: "Object") -> str:
        """Describe the node type in TypeScript notation."""
        if not isinstance(node, Object):
            raise TypeError(f"Expecting an Object node got {node}")

        code_lines = node.accept(self, depth=0)
        code = "\n".join(code_lines)
        return f"```TypeScript\n\n{code}\n```\n"


def initialize_type_descriptors(
    type_descriptor: Union[TypeDescriptor, str]
) -> TypeDescriptor:
    """Initialize the type descriptors."""
    if isinstance(type_descriptor, str):
        if type_descriptor == "bullet_point":
            return BulletPointDescriptor()
        elif type_descriptor == "typescript":
            return TypeScriptDescriptor()
        else:
            raise ValueError(
                f"Unknown type descriptor: {type_descriptor}. Use one of: bullet_point,"
                " typescript or else provide an instance of TypeDescriptor."
            )
    return type_descriptor
