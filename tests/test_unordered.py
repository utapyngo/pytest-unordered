import pytest
from pytest import raises

from pytest_unordered import _compare_eq_unordered
from pytest_unordered import unordered


@pytest.mark.parametrize('left,right', [
    (unordered([1, 2, 3]), [3, 2, 1]),
    ([3, 2, 1], unordered([1, 2, 3])),
    (unordered([1, 2, {'a': unordered([4, 5, 6])}]), [{'a': [6, 5, 4]}, 2, 1]),
    ([3, 2, {1: ['a', 'b']}], unordered([{1: ['a', 'b']}, 2, 3])),
])
def test_unordered(left, right):
    assert left == right


@pytest.mark.parametrize('value', [
    None,
    type,
    TypeError,
])
def test_unordered_non_sized_expected(value):
    with raises(TypeError):
        unordered(value)


@pytest.mark.parametrize('value', [
    None,
    type,
    TypeError,
])
def test_unordered_non_sized_actual(value):
    assert unordered([]) != value


@pytest.mark.parametrize('left,right,extra_left,extra_right', [
    ([1, 2, 3], [1, 2, 3, 4, 5], [], [4, 5]),
    ([3, 2, 1], [1, 2, 3, 4, 5], [], [4, 5]),
    ([3, 2, {1: ['a', 'b']}], [{1: ['a', 'b']}, 2, 3, 4, 5], [], [4, 5]),
    ([3, 2, {1: ['a', 'b']}], [{1: unordered(['b', 'a'])}, 2, 3, 4, 5], [], [4, 5]),
])
def test_compare_eq_unordered(left, right, extra_left, extra_right):
    assert _compare_eq_unordered(left, right) == (extra_left, extra_right)


def test_fail_nonunique(testdir):
    testdir.makepyfile(
        """
        from pytest_unordered import unordered

        def test_unordered():
            assert unordered([1, 2, 3, 3]) == [1, 2, 3]
    """
    )
    result = testdir.runpytest()
    result.assert_outcomes(failed=1, passed=0)
