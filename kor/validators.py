"""Define validator interface and provide built-in validators for common-use cases."""
import abc
from typing import Any, List, Mapping, Optional, Tuple, Type, Union

from pydantic import BaseModel, ValidationError

from ._pydantic import PYDANTIC_MAJOR_VERSION


class Validator(abc.ABC):
    @abc.abstractmethod
    def clean_data(
        self, data: Union[List[Mapping[str, Any]], Mapping[str, Any]]
    ) -> Tuple[Any, List[Exception]]:
        """Validate the data and return a cleaned version of it.

        Args:
            data: the parsed data

        Returns:
            a cleaned version of the data, the type depends on the validator
        """
        raise NotImplementedError()


class PydanticValidator(Validator):
    """Use a pydantic model for validation."""

    def __init__(self, model_class: Type[BaseModel], many: bool) -> None:
        """Create a validator for a pydantic model.

        Args:
            model_class: The pydantic model class to use for validation
            many: Whether the data is expected to correspond to a single moder
                  or a list of models
        """
        self.model_class = model_class
        self.many = many

    def clean_data(
        self, data: Any
    ) -> Tuple[Union[Optional[BaseModel], List[BaseModel]], List[Exception]]:
        """Clean the data using the pydantic model.

        Args:
            data: the parsed data

        Returns:
            cleaned data instantiated as the corresponding pydantic model
        """
        model_ = self.model_class  # a proxy to make code fit in char limit

        if self.many:
            exceptions: List[Exception] = []
            records: List[BaseModel] = []

            for item in data:
                try:
                    if PYDANTIC_MAJOR_VERSION == 1:
                        record = model_.parse_obj(item)  # type: ignore[attr-defined]
                    else:
                        record = model_.model_validate(  # type: ignore[attr-defined]
                            item
                        )

                    records.append(record)
                except ValidationError as e:
                    exceptions.append(e)
            return records, exceptions
        else:
            try:
                if PYDANTIC_MAJOR_VERSION == 1:
                    record = model_.parse_obj(data)  # type: ignore[attr-defined]
                else:
                    record = model_.model_validate(data)  # type: ignore[attr-defined]
                return record, []
            except ValidationError as e:
                return None, [e]
