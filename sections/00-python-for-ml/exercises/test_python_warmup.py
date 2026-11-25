import pytest

from python_warmup import (
    count_tokens,
    find_indices,
    pairwise_add,
    safe_slice,
    unique_in_order,
)


def test_safe_slice_and_no_aliasing():
    xs = [10.0, 20.0, 30.0, 40.0, 50.0]
    sub = safe_slice(xs, 1, 4)
    assert sub == [20.0, 30.0, 40.0]
    sub[0] = -999.0
    assert xs == [10.0, 20.0, 30.0, 40.0, 50.0]  # original list untouched
    assert safe_slice(xs, 0, 0) == []


def test_count_tokens():
    assert count_tokens(["the", "cat", "sat", "on", "the", "mat", "the"]) == {
        "the": 3,
        "cat": 1,
        "sat": 1,
        "on": 1,
        "mat": 1,
    }
    assert count_tokens([]) == {}


def test_pairwise_add():
    a = [1.0, 2.0, 3.0]
    b = [10.0, -2.0, 0.5]
    assert pairwise_add(a, b) == pytest.approx([11.0, 0.0, 3.5])
    assert pairwise_add([], []) == []
    assert a == [1.0, 2.0, 3.0] and b == [10.0, -2.0, 0.5]
    with pytest.raises(ValueError):
        pairwise_add([1.0, 2.0], [1.0])


def test_find_indices():
    assert find_indices(["a", "b", "a", "c", "a"], "a") == [0, 2, 4]
    assert find_indices([1, 2, 3], 9) == []
    assert find_indices([], "x") == []


def test_unique_in_order():
    raw = ["b", "a", "b", "c", "a", "d"]
    snap = raw[:]
    assert unique_in_order(raw) == ["b", "a", "c", "d"]
    assert raw == snap
    assert unique_in_order([]) == []
