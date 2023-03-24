"""Define validator interface and provide built-in validators for common-use cases."""
import abc
from typing import Any, Type, Union, List, Mapping
from pydantic import BaseModel


class Validator(abc.ABC):
    def is_valid(self, result) -> bool:
        """Check if the result is valid."""
        raise NotImplementedError()

    def validate_and_format(self, result) -> Any:
        """Validate and format the result."""
        raise NotImplementedError()


class PydanticValidator(Validator):
    def __init__(self, model_class: Type[BaseModel], many: bool) -> None:
        """Create a validator for a pydantic model."""
        self.model_class = model_class
        self.many = many

    def is_valid(self, result) -> bool:
        """Check if the result is valid."""
        try:
            self.model_class.validate(result)
            return True
        except Exception:
            return False

    def validate_and_format(
        self, data: Union[List[Mapping[str, Any]], Mapping[str, Any]]
    ) -> Any:
        """Validate and format the result."""
        if self.many:
            return [self.model_class(**item) for item in data]
        else:
            return self.model_class(**data)
