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

    def visit_default(self, node: "AbstractInput") -> None:
        space = "* " + self.depth * " "
        print(f"{space}{node.id}: {node.__class__.__name__} # {node.description}")

    def visit_object(self, node: ObjectInput) -> None:
        self.visit_default(node)
        self.depth += 1
        for child in node.elements:
            child.accept(self)
        self.depth -= 1
