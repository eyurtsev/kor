from kor.elements import (
    AbstractVisitor,
    ObjectInput,
    AbstractInput,
)


class TypePrinter(AbstractVisitor[None]):
    """An abstract visitor. Define here to avoid cyclical imports for now."""

    def __init__(self) -> None:
        """Use to print the type."""
        self.depth = 0
        self.type_str_messages = []

    def visit_default(self, node: "AbstractInput") -> None:
        space = "* " + self.depth * " "
        self.type_str_messages.append(
            f"{space}{node.id}: {node.__class__.__name__} # {node.description}"
        )

    def visit_object(self, node: ObjectInput) -> None:
        self.visit_default(node)
        self.depth += 1
        for child in node.elements:
            child.accept(self)
        self.depth -= 1

    def get_type(self) -> str:
        """Get the type."""
        return "\n".join(self.type_str_messages)


class TypeScriptType(AbstractVisitor[None]):
    def __init__(self) -> None:
        """Use to print the type."""
        self.depth = 0
        self.code_lines = []

    def visit_default(self, node: "AbstractInput") -> None:
        space = self.depth * " "
        self.code_lines.append(
            f"{space}{node.id}: {node.__class__.__name__} // {node.description}"
        )

    def visit_object(self, node: ObjectInput) -> None:
        space = self.depth * " "

        self.code_lines.append(f"{space}{node.id}: {{")

        self.depth += 1
        for child in node.elements:
            child.accept(self)
        self.depth -= 1

        self.code_lines.append(f"{space}}}")

    def get_type_description(self) -> str:
        """Get the type."""
        return "\n".join(self.code_lines)
