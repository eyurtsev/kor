from typing import Sequence, Mapping, Any, Union, Dict

from kor.examples import LiteralType


def _write_literal(tag_name: str, value: LiteralType) -> str:
    """Write literal."""
    return f"<{tag_name}>{value}</{tag_name}>"


def _write_list(tag_name: str, values: Sequence[LiteralType]) -> str:
    """Write list."""
    return "".join(_write_tag(tag_name, value) for value in values)


def _write_dict(tag_name: str, data: Mapping[str, Any]) -> str:
    """Write a dict."""
    s_data = "".join(
        [
            _write_tag(key, value)
            for key, value in sorted(data.items(), key=lambda item: item[0])
        ]
    )
    return _write_tag(tag_name, s_data)


def _write_tag(
    tag_name: str, data: Union[LiteralType, Sequence[LiteralType], Mapping[str, Any]]
) -> str:
    """Write a tag."""
    # Dispatch based on type.
    if isinstance(data, (str, int, float)):
        return _write_literal(tag_name, data)
    elif isinstance(data, list):
        return _write_list(tag_name, data)
    elif isinstance(data, dict):
        return _write_dict(tag_name, data)
    else:
        raise NotImplementedError(f"No support for {tag_name}")


# PUBLIC API


def encode_as_xml(obj: Dict):
    """Encode the object as XML."""
    if not isinstance(obj, dict):
        raise NotImplementedError()

    if not isinstance(obj, dict):
        raise AssertionError()

    return "".join(_write_tag(key, value) for key, value in obj.items())
