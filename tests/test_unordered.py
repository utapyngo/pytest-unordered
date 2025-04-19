from __future__ import annotations

import collections
from typing import TYPE_CHECKING
from typing import Any
from unittest.mock import ANY

import pytest

from pytest_unordered import UnorderedList
from pytest_unordered import _compare_eq_unordered
from pytest_unordered import unordered
from pytest_unordered import unordered_deep

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Mapping

    from _pytest.pytester import Pytester


@pytest.mark.parametrize(
    ("expected", "actual"),
    [
        (unordered(1, 2, 3), [3, 2, 1]),
        (unordered(1, 2, 3), (3, 2, 1)),
        (unordered(1, 2, 3), {3, 2, 1}),
        (unordered([1, 2, 3]), [3, 2, 1]),
        (unordered((1, 2, 3)), (3, 2, 1)),
        (unordered({1, 2, 3}), {3, 2, 1}),
        (unordered(1, 2, {"a": unordered(4, 5, 6)}), [{"a": [6, 5, 4]}, 2, 1]),
        (unordered([{1: unordered(["a", "b"])}, 2, 3]), [3, 2, {1: ["b", "a"]}]),
        (unordered(x for x in range(3)), [2, 1, 0]),
        (unordered(x for x in range(3)), (2, 1, 0)),
        (unordered(x for x in range(3)), {2, 1, 0}),
        (unordered(x for x in range(3)), range(3)),
        (unordered("abc"), "bac"),
        (unordered("a", "b", "c"), ["b", "a", "c"]),
        (unordered("a", "b", "c"), "bac"),
    ],
)
def test_unordered(expected: UnorderedList, actual: Iterable) -> None:
    assert expected == actual
    assert actual == expected
    assert not (expected != actual)
    assert not (actual != expected)


@pytest.mark.parametrize(
    ("left", "right"),
    [
        (unordered(2, 1, 0), (x for x in range(3))),
        ((x for x in range(3)), unordered(2, 1, 0)),
        (unordered(x for x in range(3)), (2, 1, 0)),
        ((2, 1, 0), unordered(x for x in range(3))),
        (unordered("a", "b", "c"), (x for x in "bac")),
        ((x for x in "bac"), unordered("a", "b", "c")),
    ],
)
def test_unordered_generators(left: Iterable, right: Iterable) -> None:
    # Because general generators can only be consumed once,
    # we can only do one assert
    assert left == right


@pytest.mark.parametrize(
    ("expected", "actual"),
    [
        (unordered([1, 2, 3]), [1, 2, 3, 4]),
        (unordered([1, 2, 3]), [1, 2, 3, 1]),
        (unordered([1, 2, 3]), (1, 2, 3)),
        (unordered([1, 2, 3]), {1, 2, 3}),
        (unordered([1, 2, 3]), (x + 1 for x in range(3))),
        (unordered((1, 2, 3)), (1, 2, 3, 4)),
        (unordered((1, 2, 3)), (1, 2, 3, 1)),
        (unordered((1, 2, 3)), [1, 2, 3]),
        (unordered((1, 2, 3)), {1, 2, 3}),
        (unordered((1, 2, 3)), (x + 1 for x in range(3))),
        (unordered({1, 2, 3}), {1, 2, 3, 4}),
        (unordered({1, 2, 3}), [1, 2, 3]),
        (unordered({1, 2, 3}), (1, 2, 3)),
        (unordered({1, 2, 3}), (x + 1 for x in range(3))),
        (unordered("abc"), ["b", "a", "c"]),
        (unordered("abc"), ("b", "a", "c")),
        (unordered("abc"), {"b", "a", "c"}),
    ],
)
def test_unordered_reject(expected: UnorderedList, actual: Iterable) -> None:
    assert expected != actual
    assert actual != expected
    assert not (expected == actual)
    assert not (actual == expected)


@pytest.mark.parametrize("value", [None, True, 42, object(), type, TypeError])
def test_non_sized_expected(value: Any) -> None:
    with pytest.raises(TypeError, match="cannot make unordered comparisons to non-iterable"):
        UnorderedList(value)


@pytest.mark.parametrize("value", [None, True, 42, object(), type, TypeError])
def test_non_iterable_actual(value: Any) -> None:
    assert not (unordered(1, 2, 3) == value)
    assert not (value == unordered(1, 2, 3))


@pytest.mark.parametrize(
    "value",
    [
        {1: 2, 3: 4},
        collections.defaultdict(int, a=5),
        collections.OrderedDict({1: 2, 3: 4}),
        collections.Counter("count this"),
    ],
)
def test_mapping_expected(value: Mapping) -> None:
    with pytest.raises(TypeError, match="cannot make unordered comparisons to mapping"):
        unordered(value)


@pytest.mark.parametrize("value", [None, type, TypeError])
def test_compare_to_non_sequence(value: Any) -> None:
    assert not unordered("x") == value
    assert unordered("x") != value


def test_check_type() -> None:
    assert not unordered([1]) == {1}
    assert not unordered([1], check_type=True) == {1}
    assert unordered([1], check_type=False) == {1}


@pytest.mark.parametrize(
    ("left", "right", "extra_left", "extra_right"),
    [
        ([1, 2, 3], [1, 2, 3, 4, 5], [], [4, 5]),
        ([3, 2, 1], [1, 2, 3, 4, 5], [], [4, 5]),
        ([3, 2, {1: ["a", "b"]}], [{1: ["a", "b"]}, 2, 3, 4, 5], [], [4, 5]),
        ([3, 2, {1: ["a", "b"]}], [{1: unordered("b", "a")}, 2, 3, 4, 5], [], [4, 5]),
    ],
)
def test_compare_eq_unordered(
    left: Iterable,
    right: Iterable,
    extra_left: list,
    extra_right: list,
) -> None:
    assert _compare_eq_unordered(left, right) == (extra_left, extra_right)


def test_len() -> None:
    assert len(unordered({1: ["a", "b"]}, 2, 3, 4, 5)) == 5


def test_fail_nonunique_left(pytester: Pytester) -> None:
    pytester.makepyfile(
        """
        from pytest_unordered import unordered

        def test_unordered():
            assert unordered(1, 2, 3, 3) == [1, 2, 3]
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1, passed=0)
    result.stdout.fnmatch_lines(
        [
            "E         Extra items in the left sequence:",
            "E         3",
        ],
    )


def test_fail_nonunique_right(pytester: Pytester) -> None:
    pytester.makepyfile(
        """
        from pytest_unordered import unordered

        def test_unordered():
            assert [1, 2, 3] == unordered(1, 2, 3, 3)
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1, passed=0)
    result.stdout.fnmatch_lines(
        [
            "E         Extra items in the right sequence:",
            "E         3",
        ],
    )


def test_replace(pytester: Pytester) -> None:
    pytester.makepyfile(
        """
        from pytest_unordered import unordered

        def test_unordered():
            assert [{"a": 1, "b": 2}, 2, 3] == unordered(2, 3, {"b": 2, "a": 3})
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1, passed=0)
    result.stdout.fnmatch_lines(
        [
            "E         One item replaced:",
            "E         Omitting 1 identical items, use -vv to show",
            "E         Differing items:",
            "E         {'a': 1} != {'a': 3}",
        ],
    )


def test_in(pytester: Pytester) -> None:
    pytester.makepyfile(
        """
        from pytest_unordered import unordered

        def test_unordered():
            assert 1 in unordered(2, 3)
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1, passed=0)
    result.stdout.fnmatch_lines(
        [
            "E       assert 1 in [2, 3]",
            "E        +  where [2, 3] = unordered(2, 3)",
        ],
    )


def test_type_check(pytester: Pytester) -> None:
    pytester.makepyfile(
        """
        from pytest_unordered import unordered

        def test_unordered():
            assert [3, 2, 1] == unordered((1, 2, 3))
        """,
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1, passed=0)
    result.stdout.fnmatch_lines(
        [
            "E         Type mismatch:",
            "E         <class 'list'> != <class 'tuple'>",
        ],
    )


def test_reorder_on_eq() -> None:
    unordered_list = unordered([1, 2, 3])
    assert unordered_list == [3, 1, 2]
    assert list(unordered_list) == [3, 1, 2]


def test_mock_any() -> None:
    p_unordered = {"results": unordered({"foo1": ANY}, {"foo2": ANY})}
    test_1 = {"results": [{"foo1": "value10"}, {"foo2": "value20"}]}
    test_2 = {"results": [{"foo1": "value11"}, {"foo2": "value21"}]}
    test_3 = {"results": [{"foo1": "value10"}, {"foo2": "value20"}]}
    assert p_unordered == test_1
    assert p_unordered == test_2
    assert p_unordered == test_3


@pytest.mark.parametrize(
    ("expected", "actual"),
    [
        (unordered_deep([1, 2, 3]), [3, 2, 1]),
        (unordered_deep((1, 2, 3)), (3, 2, 1)),
        (unordered_deep({1, 2, 3}), {3, 2, 1}),
        (unordered_deep([1, 2, {"a": (4, 5, 6)}]), [{"a": [6, 5, 4]}, 2, 1]),  # fmt: skip
        (unordered_deep([{1: (["a", "b"])}, 2, 3]), [3, 2, {1: ["b", "a"]}]),  # fmt: skip
        (unordered_deep(("a", "b", "c")), ["b", "a", "c"]),
    ],
)
def test_unordered_deep(expected: UnorderedList, actual: Iterable) -> None:
    assert expected == actual
    assert actual == expected
    assert not (expected != actual)
    assert not (actual != expected)
