import pytest

from python_math_drills import (
    column_sums,
    mean,
    min_max_scale,
    predict_line,
    variance,
    weighted_average,
)


def test_mean_and_variance():
    assert mean([2.0, 4.0, 6.0, 8.0]) == pytest.approx(5.0)
    # Deviations from 5.0 are [-3, -1, 1, 3] -> squared [9, 1, 1, 9] -> avg = 5.0
    assert variance([2.0, 4.0, 6.0, 8.0]) == pytest.approx(5.0)
    assert variance([7.0, 7.0, 7.0]) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        mean([])
    with pytest.raises(ValueError):
        variance([])


def test_weighted_average():
    assert weighted_average([80.0, 100.0], [1.0, 3.0]) == pytest.approx(95.0)
    assert weighted_average([10.0, 20.0], [0.0, 5.0]) == pytest.approx(20.0)
    with pytest.raises(ValueError):
        weighted_average([], [])
    with pytest.raises(ValueError):
        weighted_average([1.0, 2.0], [1.0])
    with pytest.raises(ValueError):
        weighted_average([1.0, 2.0], [0.0, 0.0])
    with pytest.raises(ValueError):
        weighted_average([1.0, 2.0], [-1.0, 2.0])


def test_min_max_scale():
    xs = [10.0, 20.0, 30.0, 50.0]
    snap = xs[:]
    assert min_max_scale(xs) == pytest.approx([0.0, 0.25, 0.5, 1.0])
    assert xs == snap
    # Constant input must not divide by zero
    assert min_max_scale([5.0, 5.0, 5.0]) == pytest.approx([0.0, 0.0, 0.0])
    with pytest.raises(ValueError):
        min_max_scale([])


def test_predict_line():
    assert predict_line([0.0, 1.0, 2.0, 3.0], w=2.0, b=1.0) == pytest.approx([1.0, 3.0, 5.0, 7.0])
    assert predict_line([], w=2.0, b=1.0) == []


def test_column_sums():
    grid = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
    ]
    assert column_sums(grid) == pytest.approx([5.0, 7.0, 9.0])
    assert column_sums([[10.0]]) == pytest.approx([10.0])
    with pytest.raises(ValueError):
        column_sums([])
    with pytest.raises(ValueError):
        column_sums([[]])
    with pytest.raises(ValueError):
        column_sums([[1.0, 2.0], [3.0]])
