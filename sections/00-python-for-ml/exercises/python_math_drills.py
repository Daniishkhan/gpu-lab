"""Doing everyday math in plain Python: formulas, stats & 2D grids.

Topic: 00.02

Math equations stop looking intimidating once you translate them into 3–5 lines of
plain Python and test them on 4 small numbers. Practice the exact math formulas
and 2D grid loops that prepare you for NumPy and Stage 1 gradient descent.

Say it out loud:
  1. Why is `[[0] * 3] * 2` a dangerous way to build a 2×3 grid in Python?
  2. What does variance measure in plain English, and why do we square `(x - mean)`?
  3. How does `predict_line(xs, w, b)` connect directly to fitting a line in Stage 1?
"""
from __future__ import annotations

from collections.abc import Sequence


def mean(xs: Sequence[float]) -> float:
    """Return the arithmetic average sum(xs) / len(xs). Raise ValueError if empty."""
    raise NotImplementedError


def weighted_average(values: Sequence[float], weights: Sequence[float]) -> float:
    """Return sum(v * w) / sum(weights).

    Raise ValueError if empty, lengths differ, any weight < 0, or sum(weights) <= 0.
    """
    raise NotImplementedError


def variance(xs: Sequence[float]) -> float:
    """Return population variance: mean of (x - mean(xs))^2 across all x in xs.

    Raise ValueError if `xs` is empty.
    """
    raise NotImplementedError


def min_max_scale(xs: Sequence[float]) -> list[float]:
    """Rescale values linearly to [0.0, 1.0]: (x - min_x) / (max_x - min_x).

    If all values are identical (max_x == min_x), return a list of 0.0s of the same length.
    Raise ValueError if `xs` is empty. Must not mutate `xs`.
    """
    raise NotImplementedError


def predict_line(xs: Sequence[float], w: float, b: float) -> list[float]:
    """Return [w * x + b for x in xs] as floats. Must not mutate `xs`."""
    raise NotImplementedError


def column_sums(grid: Sequence[Sequence[float]]) -> list[float]:
    """Return a list with the sum of each column in a rectangular 2D `grid`.

    Example:
      [[1, 2, 3],
       [4, 5, 6]] -> [5.0, 7.0, 9.0]

    Raise ValueError if `grid` is empty, has empty rows, or is ragged (rows differ in length).
    """
    raise NotImplementedError
