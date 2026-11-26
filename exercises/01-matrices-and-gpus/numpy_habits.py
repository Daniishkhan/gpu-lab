"""Everyday NumPy habits in plain Python: slicing, axis, broadcasting & masks.

Topic: 01.03

Build the exact mental model behind the five NumPy operations you use every day in ML:
  1. Column slicing:      M[:, col]
  2. Axis reductions:     M.sum(axis=0) (down columns) vs. M.sum(axis=1) (across rows)
  3. Row broadcasting:    X + bias (adding a 1D vector to every row of a 2D matrix)
  4. Boolean filtering:   np.maximum(x, 0.0) (your first taste of ReLU!)
  5. Causal masking:      hiding future columns (col > row) with -inf before softmax

Say it out loud:
  1. On a 2D matrix of shape (rows, cols), what shape does sum(axis=0) return vs. sum(axis=1)?
  2. When you write `X + bias` for shape (3, 4) and (4,), how does broadcasting line them up?
  3. Why do LLMs mask positions where `col > row` to `-inf`?
"""
from __future__ import annotations

import math
from collections.abc import Sequence


def get_column(grid: Sequence[Sequence[float]], col: int) -> list[float]:
    """Return column `col` as a NEW list (equivalent to NumPy's `grid[:, col]`).

    Supports negative column indexing (e.g. col=-1 for last column).
    Raise ValueError if grid is empty, ragged, or `col` is out of bounds.
    """
    raise NotImplementedError


def sum_axis(grid: Sequence[Sequence[float]], axis: int) -> list[float]:
    """Sum a rectangular 2D matrix along `axis`:
      - axis == 0: sum DOWN each column -> length == num_cols
      - axis == 1: sum ACROSS each row  -> length == num_rows

    Raise ValueError if grid is empty, ragged, or axis is not 0 or 1.
    """
    raise NotImplementedError


def add_row_bias(
    grid: Sequence[Sequence[float]],
    bias: Sequence[float],
) -> list[list[float]]:
    """Add 1D `bias` (length C) to EVERY row of 2D `grid` (shape R × C) -> NEW (R × C) list.

    (Equivalent to NumPy's broadcasted `grid + bias`.)
    Raise ValueError if grid is empty/ragged or len(bias) != num_cols.
    Must not mutate `grid` or `bias`.
    """
    raise NotImplementedError


def relu_mask(xs: Sequence[float]) -> list[float]:
    """Return NEW list replacing negative numbers with 0.0 (equivalent to `np.maximum(xs, 0.0)`).

    Must not mutate `xs`.
    """
    raise NotImplementedError


def causal_mask(
    scores: Sequence[Sequence[float]],
    mask_value: float = -math.inf,
) -> list[list[float]]:
    """Return NEW square (T × T) matrix with future positions (col > row) set to `mask_value`.

    Past and current positions (col <= row) keep their original value.
    Raise ValueError if `scores` is empty, ragged, or not square. Must not mutate `scores`.
    """
    raise NotImplementedError
