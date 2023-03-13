import pytest

from kor.nodes import (
    AbstractVisitor,
    AbstractInput,
    Number,
    Text,
    Option,
    Selection,
    Object,
)

from kor.examples import _write_tag


def test_write_tag():
    assert _write_tag("tag", "data") == "<tag>data</tag>"
    assert _write_tag("tag", ['data1', 'data2']) == "<tag>data</tag>"
