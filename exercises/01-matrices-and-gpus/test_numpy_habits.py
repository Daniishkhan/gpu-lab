import math
import pytest

from numpy_habits import (
    add_row_bias,
    causal_mask,
    get_column,
    relu_mask,
    sum_axis,
)


def test_get_column():
    grid = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
    ]
    assert get_column(grid, 1) == [2.0, 5.0]
    assert get_column(grid, -1) == [3.0, 6.0]
    with pytest.raises(ValueError):
        get_column(grid, 3)
    with pytest.raises(ValueError):
        get_column(grid, -4)
    with pytest.raises(ValueError):
        get_column([], 0)
    with pytest.raises(ValueError):
        get_column([[1.0, 2.0], [3.0]], 0)


def test_sum_axis():
    grid = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
    ]
    # axis=0 collapses rows -> 3 column totals
    assert sum_axis(grid, axis=0) == pytest.approx([5.0, 7.0, 9.0])
    # axis=1 collapses columns -> 2 row totals
    assert sum_axis(grid, axis=1) == pytest.approx([6.0, 15.0])
    with pytest.raises(ValueError):
        sum_axis(grid, axis=2)
    with pytest.raises(ValueError):
        sum_axis([], axis=0)


def test_add_row_bias_broadcast():
    grid = [
        [1.0, 2.0, 3.0],
        [10.0, 20.0, 30.0],
    ]
    bias = [0.5, -1.0, 2.0]
    snap = [r[:] for r in grid]
    out = add_row_bias(grid, bias)
    assert grid == snap  # must not mutate caller grid
    assert out == [[1.5, 1.0, 5.0], [10.5, 19.0, 32.0]]

    with pytest.raises(ValueError):
        add_row_bias(grid, [1.0, 2.0])  # wrong bias length
    with pytest.raises(ValueError):
        add_row_bias([], bias)


def test_relu_mask():
    xs = [-3.0, 0.0, 2.5, -0.1, 4.0]
    snap = xs[:]
    assert relu_mask(xs) == pytest.approx([0.0, 0.0, 2.5, 0.0, 4.0])
    assert xs == snap
    assert relu_mask([]) == []


def test_causal_mask():
    scores = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0],
    ]
    snap = [r[:] for r in scores]
    masked = causal_mask(scores)
    assert scores == snap
    assert masked[0] == [1.0, -math.inf, -math.inf]
    assert masked[1] == [4.0, 5.0, -math.inf]
    assert masked[2] == [7.0, 8.0, 9.0]
    assert causal_mask(scores, mask_value=0.0)[0] == [1.0, 0.0, 0.0]

    with pytest.raises(ValueError):
        causal_mask([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    with pytest.raises(ValueError):
        causal_mask([])
