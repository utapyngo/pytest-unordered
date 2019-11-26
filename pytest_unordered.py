from typing import Sized

from _pytest._io.saferepr import saferepr


class Unordered:
    def __init__(self, expected):
        if not isinstance(expected, Sized):
            raise TypeError(
                "cannot make unordered comparisons to non-sized values: {!r}".format(
                    expected
                )
            )
        self.expected = expected

    def __eq__(self, actual):
        if not isinstance(actual, Sized):
            return self.expected == actual
        if len(actual) != len(self.expected):
            return False
        extra_left, extra_right = _compare_eq_unordered(self.expected, actual)
        return not extra_left and not extra_right

    def __repr__(self):
        return "unordered({!r})".format(self.expected)

    def __len__(self):
        return len(self.expected)

    def __iter__(self):
        return iter(self.expected)


def unordered(expected):
    return Unordered(expected)


def _compare_eq_unordered(left, right):
    extra_left = []
    extra_right = list(right)
    for elem in left:
        try:
            extra_right.remove(elem)
        except ValueError:
            extra_left.append(elem)
    return extra_left, extra_right


def pytest_assertrepr_compare(op, left, right):
    if (isinstance(left, Unordered) or isinstance(right, Unordered)) and op == "==":
        if isinstance(left, Unordered):
            left = left.expected
        if isinstance(right, Unordered):
            right = right.expected
        left_repr = saferepr(left)
        right_repr = saferepr(right)
        result = ["{} {} {}".format(left_repr, op, right_repr)]
        extra_left, extra_right = _compare_eq_unordered(left, right)
        if extra_left:
            result.append("Extra items in the left sequence:")
            for item in extra_left:
                result.append(saferepr(item))
        if extra_right:
            result.append("Extra items in the right sequence:")
            for item in extra_right:
                result.append(saferepr(item))
        return result
