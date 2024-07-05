from typing import Any
from typing import Generator
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional
from typing import Tuple

import pytest
from _pytest._io.saferepr import saferepr
from _pytest.assertion.util import _compare_eq_any
from _pytest.config import Config


class UnorderedList(list):
    def __init__(self, expected: Iterable, check_type: bool = True):
        if not isinstance(expected, Iterable):
            raise TypeError(
                "cannot make unordered comparisons to non-iterable: {!r}".format(expected)
            )
        if isinstance(expected, Mapping):
            raise TypeError("cannot make unordered comparisons to mapping: {!r}".format(expected))
        super().__init__(expected)
        self._expected_type = type(expected) if check_type else None

    def __eq__(self, actual: object) -> bool:
        if self._expected_type is not None and self._expected_type != type(actual):
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

    def compare_to(self, other: List) -> Tuple[List, List]:
        extra_left = list(self)
        extra_right = []
        reordered = []
        placeholder = object()
        for elem in other:
            try:
                i = extra_left.index(elem)
                matched_element = extra_left[i]
                del extra_left[i]
                reordered.append(matched_element)
            except ValueError:
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


def unordered(*args: Any, check_type: Optional[bool] = None) -> UnorderedList:
    if len(args) == 1:
        if check_type is None:
            check_type = not isinstance(args[0], Generator)
        return UnorderedList(args[0], check_type=check_type)
    return UnorderedList(args, check_type=False)


def _compare_eq_unordered(left: Iterable, right: Iterable) -> Tuple[List, List]:
    extra_left = []
    extra_right = list(right)
    for elem in left:
        try:
            extra_right.remove(elem)
        except ValueError:
            extra_left.append(elem)
    return extra_left, extra_right


def pytest_assertrepr_compare(
    config: Config, op: str, left: Any, right: Any
) -> Optional[List[str]]:
    if (isinstance(left, UnorderedList) or isinstance(right, UnorderedList)) and op == "==":
        verbose = config.getoption("verbose")
        left_repr = saferepr(left)
        right_repr = saferepr(right)
        result = ["{} {} {}".format(left_repr, op, right_repr)]
        left_type = left._expected_type if isinstance(left, UnorderedList) else type(left)
        right_type = right._expected_type if isinstance(right, UnorderedList) else type(right)
        if left_type and right_type and left_type != right_type:
            result.append("Type mismatch:")
            result.append("{} != {}".format(left_type, right_type))
        extra_left, extra_right = _compare_eq_unordered(left, right)
        if len(extra_left) == 1 and len(extra_right) == 1:
            result.append("One item replaced:")
            if pytest.version_tuple < (8, 0, 0):
                result.extend(
                    _compare_eq_any(extra_left[0], extra_right[0], verbose=verbose)  # type: ignore
                )
            else:
                result.extend(
                    _compare_eq_any(
                        extra_left[0],
                        extra_right[0],
                        highlighter=config.get_terminal_writer()._highlight,
                        verbose=verbose,
                    )
                )
        else:
            if extra_left:
                result.append("Extra items in the left sequence:")
                for item in extra_left:
                    result.append(saferepr(item))
            if extra_right:
                result.append("Extra items in the right sequence:")
                for item in extra_right:
                    result.append(saferepr(item))
        return result
    return None
