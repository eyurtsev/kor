import abc
import dataclasses
from typing import List, Mapping, Optional


@dataclasses.dataclass(frozen=True)
class SExpr(abc.ABC):
    pass


@dataclasses.dataclass(frozen=True)
class Number(SExpr):
    value: float | int

    def __str__(self) -> str:
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class String(SExpr):
    value: str

    def __str__(self) -> str:
        return f'"{self.value}"'


@dataclasses.dataclass(frozen=True)
class SList(SExpr):
    elements: List[SExpr]

    def __str__(self) -> str:
        return f'({" ".join(str(elem) for elem in self.elements)})'


@dataclasses.dataclass(frozen=True)
class Object(SExpr):
    properties: Mapping[str, SExpr]

    def __str__(self) -> str:
        return (
            f'{{{", ".join(f"{key}: {str(value)}" for key, value in self.properties)}}}'
        )


@dataclasses.dataclass(frozen=True)
class Function(SExpr):
    name: str
    params: List[SExpr]
    return_type: Optional[SExpr]

    def __str__(self) -> str:
        params_str = " ".join(str(param) for param in self.params)
        return_type_str = f" -> {str(self.return_type)}" if self.return_type else ""
        return f"({self.name} {params_str}{return_type_str})"


@dataclasses.dataclass(frozen=True)
class TypeAnnotation(SExpr):
    value: SExpr

    def __str__(self) -> str:
        """Return the string representation of the type annotation."""
        return self.value.__class__.__name__
