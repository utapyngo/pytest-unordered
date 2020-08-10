# pytest-unordered

[![Build Status](https://travis-ci.org/utapyngo/pytest-unordered.svg?branch=master)](https://travis-ci.org/utapyngo/pytest-unordered)
[![Coverage Status](https://coveralls.io/repos/github/utapyngo/pytest-unordered/badge.svg?branch=master)](https://coveralls.io/github/utapyngo/pytest-unordered?branch=master)

Test equality of unordered collections in pytest.

## Installation

    pip install pytest-unordered
    

## Usage

    from pytest_unordered import unordered
    
    def test_unordered():
        assert [3, 2, {1: ['b', 'a']}] == unordered({1: unordered('a', 'b')}, 2, 3)
