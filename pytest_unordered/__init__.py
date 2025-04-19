from __future__ import annotations

from collections.abc import Generator
from collections.abc import Iterable
from collections.abc import Mapping
from typing import TYPE_CHECKING
from typing import Any

import pytest
from _pytest._io.saferepr import saferepr
from _pytest.assertion.util import _compare_eq_any

if TYPE_CHECKING:
    from _pytest.config import Config


class UnorderedList(list):
    def __init__(self, expected: Iterable, *, check_type: bool = True) -> None:
        if not isinstance(expected, Iterable):
            msg = f"cannot make unordered comparisons to non-iterable: {expected!r}"
            raise TypeError(
                msg,
            )
        if isinstance(expected, Mapping):
            msg = f"cannot make unordered comparisons to mapping: {expected!r}"
            raise TypeError(msg)
        super().__init__(expected)
        self.expected_type = type(expected) if check_type else None

    def __eq__(self, actual: object) -> bool:
        if self.expected_type is not None and self.expected_type is not type(actual):
            return False
        if not isinstance(actual, Iterable):
            return self.copy() == actual
        actual_list = list(actual)
        if len(actual_list) != len(self):
            return False
        extra_left, extra_right = self.compare_to(actual_list)
        return not extra_left and not extra_right

    def __ne__(self, actual: object) -> bool:
        return not (self == actual)

    def compare_to(self, other: list) -> tuple[list, list]:
        extra_left = list(self)
        extra_right: list[Any] = []
        reordered: list[Any] = []
        placeholder = object()
        for elem in other:
            if elem in extra_left:
                i = extra_left.index(elem)
                reordered.append(extra_left.pop(i))
            else:
                extra_right.append(elem)
                reordered.append(placeholder)
        placeholder_fillers = extra_left.copy()
        for i, elem in reversed(list(enumerate(reordered))):
            if not placeholder_fillers:
                break
            if elem == placeholder:
                reordered[i] = placeholder_fillers.pop()
        self[:] = [e for e in reordered if e is not placeholder]
        return extra_left, extra_right


def unordered(*args: Any, check_type: bool | None = None) -> UnorderedList:
    if len(args) == 1:
        if check_type is None:
            check_type = not isinstance(args[0], Generator)
        return UnorderedList(args[0], check_type=check_type)
    return UnorderedList(args, check_type=False)


def unordered_deep(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: unordered_deep(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return unordered(unordered_deep(x) for x in obj)
    return obj


def _compare_eq_unordered(left: Iterable, right: Iterable) -> tuple[list, list]:
    extra_left: list[Any] = []
    extra_right = list(right)
    for elem in left:
        if elem in extra_right:
            extra_right.remove(elem)
        else:
            extra_left.append(elem)
    return extra_left, extra_right


def pytest_assertrepr_compare(
    config: Config,
    op: str,
    left: Any,
    right: Any,
) -> list[str] | None:
    if (isinstance(left, UnorderedList) or isinstance(right, UnorderedList)) and op == "==":
        verbose = config.getoption("verbose")
        left_repr = saferepr(left)
        right_repr = saferepr(right)
        result = [f"{left_repr} {op} {right_repr}"]
        left_type = left.expected_type if isinstance(left, UnorderedList) else type(left)
        right_type = right.expected_type if isinstance(right, UnorderedList) else type(right)
        if left_type and right_type and left_type != right_type:
            result.append("Type mismatch:")
            result.append(f"{left_type} != {right_type}")
        extra_left, extra_right = _compare_eq_unordered(left, right)
        if len(extra_left) == 1 and len(extra_right) == 1:
            result.append("One item replaced:")
            if pytest.version_tuple < (8, 0, 0):  # pragma: no cover
                result.extend(
                    _compare_eq_any(extra_left[0], extra_right[0], verbose=verbose),  # type: ignore[call-arg]
                )
            else:
                result.extend(
                    _compare_eq_any(
                        extra_left[0],
                        extra_right[0],
                        highlighter=config.get_terminal_writer()._highlight,  # noqa: SLF001
                        verbose=verbose,
                    ),
                )
        else:
            if extra_left:
                result.append("Extra items in the left sequence:")
                result.extend(saferepr(item) for item in extra_left)
            if extra_right:
                result.append("Extra items in the right sequence:")
                result.extend(saferepr(item) for item in extra_right)
        return result
    return None
