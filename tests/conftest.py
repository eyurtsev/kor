import operator
from typing import Any, List, Optional, cast

from kor.nodes import AbstractSchemaNode, Object, _get_all_slots


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
        if type(left) != type(right):
            return [
                "Comparing AbstractSchemaNode instances:",
                f"Type mismatch: {type(left)} ({left.id}) != "
                f"{type(right)} ({right.id})",
            ]

        all_slots = _get_all_slots(left)

        attr_getters = [
            (attr, operator.attrgetter(attr))
            for attr in all_slots
            if attr != "attributes"
        ]

        if "attributes" in all_slots:
            if not isinstance(left, Object) and not isinstance(right, Object):
                raise AssertionError("Expected both nodes to be of type Object")
            left = cast(Object, left)
            right = cast(Object, right)
            if len(left.attributes) != len(right.attributes):
                return [
                    "Comparing AbstractSchemaNode instances:",
                    f"attributes: {left.attributes} != {right.attributes}",
                ]
            for attr1, attr2 in zip(left.attributes, right.attributes):
                if attr1 != attr2:
                    return pytest_assertrepr_compare(op, attr1, attr2)

        return [
            "Comparing AbstractSchemaNode instances:",
            f"{left}: "
            + ", ".join([f"{attr}: {getter(left)}" for attr, getter in attr_getters]),
            f"{right}: "
            + ", ".join([f"{attr}: {getter(right)}" for attr, getter in attr_getters]),
        ]
    return None
