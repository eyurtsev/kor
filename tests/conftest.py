from typing import List, Optional, Any

import operator

from kor.nodes import AbstractSchemaNode, _get_all_slots


def pytest_assertrepr_compare(op: str, left: Any, right: Any) -> Optional[List[str]]:
    """Temporary implementation of custom fail messages for schema nodes.

    This code will go away once it is decided what to use for modeling schema nodes
    instead of vanilla python classes.
    """
    if (
        isinstance(left, AbstractSchemaNode)
        and isinstance(right, AbstractSchemaNode)
        and op == "=="
    ):
        all_slots = _get_all_slots(left)
        attr_getters = [(attr, operator.attrgetter(attr)) for attr in all_slots]

        return [
            "Comparing AbstractSchemaNode instances:",
            ", ".join([f"{attr}: {getter(left)}" for attr, getter in attr_getters]),
            ", ".join([f"{attr}: {getter(right)}" for attr, getter in attr_getters]),
        ]
