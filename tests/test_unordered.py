import pytest
from pytest import raises

from pytest_unordered import UnorderedList
from pytest_unordered import _compare_eq_unordered
from pytest_unordered import unordered


@pytest.mark.parametrize(
    "left,right",
    [
        (unordered(1, 2, 3), [3, 2, 1]),
        ([3, 2, 1], unordered(1, 2, 3)),
        (unordered(1, 2, {"a": unordered(4, 5, 6)}), [{"a": [6, 5, 4]}, 2, 1]),
        ([3, 2, {1: ["a", "b"]}], unordered({1: ["a", "b"]}, 2, 3)),
    ],
)
def test_unordered(left, right):
    assert left == right


@pytest.mark.parametrize("value", [None, type, TypeError])
def test_non_sized_expected(value):
    with raises(TypeError):
        UnorderedList(value)


@pytest.mark.parametrize("value", [None, type, TypeError])
def test_compare_to_non_sequence(value):
    assert not unordered("x") == value
    assert unordered("x") != value


@pytest.mark.parametrize(
    "left,right,extra_left,extra_right",
    [
        ([1, 2, 3], [1, 2, 3, 4, 5], [], [4, 5]),
        ([3, 2, 1], [1, 2, 3, 4, 5], [], [4, 5]),
        ([3, 2, {1: ["a", "b"]}], [{1: ["a", "b"]}, 2, 3, 4, 5], [], [4, 5]),
        ([3, 2, {1: ["a", "b"]}], [{1: unordered("b", "a")}, 2, 3, 4, 5], [], [4, 5]),
    ],
)
def test_compare_eq_unordered(left, right, extra_left, extra_right):
    assert _compare_eq_unordered(left, right) == (extra_left, extra_right)


def test_len():
    assert len(unordered({1: ["a", "b"]}, 2, 3, 4, 5)) == 5


def test_fail_nonunique_left(testdir):
    testdir.makepyfile(
        """
        from pytest_unordered import unordered

        def test_unordered():
            assert unordered(1, 2, 3, 3) == [1, 2, 3]
    """
    )
    result = testdir.runpytest()
    result.assert_outcomes(failed=1, passed=0)
    result.stdout.fnmatch_lines([
        "E         Extra items in the left sequence:",
        "E         3",
    ])


def test_fail_nonunique_right(testdir):
    testdir.makepyfile(
        """
        from pytest_unordered import unordered

        def test_unordered():
            assert [1, 2, 3] == unordered(1, 2, 3, 3)
    """
    )
    result = testdir.runpytest()
    result.assert_outcomes(failed=1, passed=0)
    result.stdout.fnmatch_lines([
        "E         Extra items in the right sequence:",
        "E         3"
    ])


def test_replace(testdir):
    testdir.makepyfile(
        """
        from pytest_unordered import unordered

        def test_unordered():
            assert [{"a": 1, "b": 2}, 2, 3] == unordered(2, 3, {"b": 2, "a": 3})
    """
    )
    result = testdir.runpytest()
    result.assert_outcomes(failed=1, passed=0)
    result.stdout.fnmatch_lines([
        "E         One item replaced:",
        "E         Omitting 1 identical items, use -vv to show",
        "E         Differing items:",
        "E         {'a': 1} != {'a': 3}",
        "E         Use -v to get the full diff",
    ])


def test_in(testdir):
    testdir.makepyfile(
        """
        from pytest_unordered import unordered

        def test_unordered():
            assert 1 in unordered(2, 3)
    """
    )
    result = testdir.runpytest()
    result.assert_outcomes(failed=1, passed=0)
    result.stdout.fnmatch_lines([
        "E       assert 1 in [2, 3]",
        "E        +  where [2, 3] = unordered(2, 3)",
    ])
