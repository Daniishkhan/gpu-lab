"""Vectors, distance, dot products & cosine similarity in plain Python.

Topic: 01.01

Build core vector math directly from the zip() and sum() habits you practiced in
Subject 00. Once these six small functions click in plain Python, NumPy's `u + v`,
`scalar * u`, and `u @ v` will feel completely transparent.

Say it out loud:
  1. Geometrically, what does a positive vs. zero vs. negative dot product tell you?
  2. Why can two vectors have a large dot product yet point in slightly different directions,
     and how does cosine similarity fix that?
  3. How do `vec_add(u, v)` and `dot_product(u, v)` translate into 1-line NumPy?
"""
from __future__ import annotations

from collections.abc import Sequence


def vec_add(a: Sequence[float], b: Sequence[float]) -> list[float]:
    """Return NEW list [a[i] + b[i]]. Raise ValueError if empty or lengths differ."""
    raise NotImplementedError


def vec_scale(v: Sequence[float], scalar: float) -> list[float]:
    """Return NEW list [scalar * x for x in v]. Raise ValueError if empty."""
    raise NotImplementedError


def l1_norm(v: Sequence[float]) -> float:
    """Return sum(|x| for x in v). Raise ValueError if empty."""
    raise NotImplementedError


def l2_norm(v: Sequence[float]) -> float:
    """Return Euclidean length sqrt(sum(x^2)). Raise ValueError if empty."""
    raise NotImplementedError


def euclidean_distance(a: Sequence[float], b: Sequence[float]) -> float:
    """Return sqrt(sum((a[i] - b[i])^2)). Raise ValueError if empty or lengths differ."""
    raise NotImplementedError


def dot_product(a: Sequence[float], b: Sequence[float]) -> float:
    """Return sum(a[i] * b[i]). Raise ValueError if empty or lengths differ."""
    raise NotImplementedError


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Return dot_product(a, b) / (l2_norm(a) * l2_norm(b)) in [-1.0, 1.0].

    Raise ValueError if empty, lengths differ, or either vector has zero L2 norm.
    """
    raise NotImplementedError
