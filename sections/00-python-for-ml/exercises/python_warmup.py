"""Python refresher & everyday idioms for ML scripts.

Topic: 00.01

Before touching NumPy or PyTorch, warm up your fingers on the five everyday Python
building blocks that show up in almost every ML file:
  1. Slicing & copying (without accidentally mutating the caller's list)
  2. Counting items cleanly with dictionaries
  3. Combining two lists element-by-element with zip()
  4. Tracking positions with enumerate()
  5. Deduplicating with a set while keeping original order

Say it out loud:
  1. Why can writing `b = a` and then `b.append(1)` cause a bug even if you never touched `a`?
  2. How does `zip(a, b)` behave if `a` and `b` have different lengths unless you check?
  3. Why is checking `x in seen` on a `set` much faster than on a `list` for 100,000 items?
"""
from __future__ import annotations

from collections.abc import Sequence


def safe_slice(xs: Sequence[float], start: int, end: int) -> list[float]:
    """Return a NEW list containing xs[start:end]. Must not mutate `xs`."""
    raise NotImplementedError


def count_tokens(tokens: Sequence[str]) -> dict[str, int]:
    """Return a dict mapping each distinct string in `tokens` to its occurrence count.

    Example: ["cat", "dog", "cat"] -> {"cat": 2, "dog": 1}
    Empty input returns {}.
    """
    raise NotImplementedError


def pairwise_add(a: Sequence[float], b: Sequence[float]) -> list[float]:
    """Return a NEW list [a[0] + b[0], a[1] + b[1], ...] using zip().

    Raise ValueError if len(a) != len(b). Must not mutate `a` or `b`.
    """
    raise NotImplementedError


def find_indices(items: Sequence[object], target: object) -> list[int]:
    """Return all 0-based indices where `items[i] == target`, in ascending order.

    Hint: enumerate(items) gives you (index, value) pairs cleanly.
    """
    raise NotImplementedError


def unique_in_order(items: Sequence[object]) -> list[object]:
    """Return a NEW list with duplicates removed, preserving first-seen order.

    Example: ["b", "a", "b", "c", "a"] -> ["b", "a", "c"]
    Must not mutate `items`.
    """
    raise NotImplementedError
