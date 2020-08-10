from typing import Iterable
from typing import Sequence

from _pytest._io.saferepr import saferepr
from _pytest.assertion.util import _compare_eq_any


class UnorderedList(list):
    def __init__(self, expected: Sequence):
        if not isinstance(expected, Sequence):
            raise TypeError(
                "cannot make unordered comparisons to non-collections: {!r}".format(expected)
            )
        super().__init__(expected)

    def __eq__(self, actual: Sequence) -> bool:
        if not isinstance(actual, Sequence):
            return self.copy() == actual
        if len(actual) != len(self):
            return False
        extra_left, extra_right = _compare_eq_unordered(self, actual)
        return not extra_left and not extra_right


def unordered(*args):
    return UnorderedList(args)


def _compare_eq_unordered(left: Iterable, right: Iterable):
    extra_left = []
    extra_right = list(right)
    for elem in left:
        try:
            extra_right.remove(elem)
        except ValueError:
            extra_left.append(elem)
    return extra_left, extra_right


def pytest_assertrepr_compare(config, op, left, right):
    if (isinstance(left, UnorderedList) or isinstance(right, UnorderedList)) and op == "==":
        verbose = config.getoption("verbose")
        left_repr = saferepr(left)
        right_repr = saferepr(right)
        result = ["{} {} {}".format(left_repr, op, right_repr)]
        extra_left, extra_right = _compare_eq_unordered(left, right)
        if len(extra_left) == 1 and len(extra_right) == 1:
            result.append("One item replaced:")
            result.extend(_compare_eq_any(extra_left[0], extra_right[0], verbose))
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
