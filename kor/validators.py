"""Define validator interface and provide built-in validators for common-use cases."""
import abc
from pydantic import BaseModel
from typing import Any, Type, Union, List, Mapping


class Validator(abc.ABC):
    @abc.abstractmethod
    def clean_data(
        self, data: Union[List[Mapping[str, Any]], Mapping[str, Any]]
    ) -> Any:
        """Validate the data and return a cleaned version of it.

        Args:
            data: the parsed data

        Returns:
            a cleaned version of the data, the type depends on the validator
        """
        raise NotImplementedError()


class PydanticValidator(Validator):
    """Use a pydantic model for validation."""

    def __init__(self, model_class: Type[BaseModel]) -> None:
        """Create a validator for a pydantic model.

        Args:
            model_class: The pydantic model class to use for validation
        """
        self.model_class = model_class

    def clean_data(self, data: Mapping[str, Any]) -> Union[List[BaseModel], BaseModel]:
        """Clean the data using the pydantic model.

        Args:
            data: the parsed data

        Returns:
            cleaned data instantiated as the corresponding pydantic model
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected a dictionary got {type(data)}")
        return self.model_class(**data)
