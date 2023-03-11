"""Code that takes a object_input and outputs a string that describes its schema.

Without fine-tuning the LLM, the quality of the response may end up depending
on details such as the schema description in the prompt.

Designing the code here to make it easier to experiment with different ways
of describing the schema.
"""
from kor.nodes import AbstractInput, AbstractVisitor, Number, Object, Selection, Text


class BulletPointTypeGenerator(AbstractVisitor[None]):
    """Mutable visitor used to generate a bullet point style schema description."""

    def __init__(self) -> None:
        self.depth = 0
        self.type_str_messages = []

    def visit_default(self, node: "AbstractInput") -> None:
        """Default action for a node."""
        space = "* " + self.depth * " "
        self.type_str_messages.append(
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
        return "\n".join(self.type_str_messages)


class TypeScriptTypeGenerator(AbstractVisitor[None]):
    """A mutable visitor (not thread safe) that helps generate TypeScript schema."""

    def __init__(self) -> None:
        self.depth = 0
        self.code_lines = []

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

        self.code_lines.append(
            f"{space}{node.id}: {finalized_type}[] // {node.description}"
        )

    def visit_object(self, node: Object) -> None:
        """Visit an object node."""
        space = self.depth * " "

        self.code_lines.append(f"{space}{node.id}: {{")

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
        return self.get_type_description()


# PUBLIC API


def generate_bullet_point_description(node: AbstractInput) -> str:
    """Generate type description for the node in a custom bullet point format."""
    code_generator = BulletPointTypeGenerator()
    node.accept(code_generator)
    return code_generator.get_type_description()


def generate_typescript_description(node: AbstractInput) -> str:
    """Generate a description of the object_input type in TypeScript syntax."""
    code_generator = TypeScriptTypeGenerator()
    type_script_code = code_generator.describe(node)
    return f"```TypeScript\n\n{type_script_code}\n```\n"
