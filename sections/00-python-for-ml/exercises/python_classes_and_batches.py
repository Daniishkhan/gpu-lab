"""Practical Python classes, magic methods & batch generators for ML.

Topic: 00.03

When you open Stage 1's micro_autograd.py or PyTorch's nn.Module and DataLoader,
you'll see four clean Python patterns over and over:
  1. Small classes holding values (`Vec2D` with __init__, __repr__, __add__, __mul__)
  2. Callable objects (`LinearScaler` with __call__ so `layer(x)` works like a function)
  3. Indexable containers (`TinyDataset` with __len__ and __getitem__)
  4. Batch generators (`batch_iter` using `yield` to serve one mini-batch at a time)

Say it out loud:
  1. What Python method runs behind the scenes when you write `a + b` or `model(x)`?
  2. Why should `a + b` return a NEW Vec2D instead of overwriting `a.x` and `a.y`?
  3. What is the difference between `return` and `yield` inside `batch_iter`?
"""
from __future__ import annotations

from collections.abc import Iterator, Sequence


class Vec2D:
    """Simple immutable 2D vector supporting +, *, ==, and readable repr.

    Attributes:
      x: float
      y: float

    Methods:
      - __init__(self, x: float, y: float) -> stores float(x), float(y)
      - __repr__(self) -> e.g. "Vec2D(1.0, 2.0)" (must start with "Vec2D(")
      - __eq__(self, other) -> True iff other is Vec2D with same x and y
      - __add__(self, other: Vec2D) -> NEW Vec2D(self.x + other.x, self.y + other.y)
      - __mul__(self, scalar: int | float) -> NEW Vec2D(self.x * scalar, self.y * scalar)
    """

    def __init__(self, x: float, y: float) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    def __add__(self, other: Vec2D) -> Vec2D:
        raise NotImplementedError

    def __mul__(self, scalar: int | float) -> Vec2D:
        raise NotImplementedError


class LinearScaler:
    """Callable layer computing w * x + b (preview of PyTorch nn.Module.__call__).

    Example:
      layer = LinearScaler(w=2.0, b=1.0)
      layer(3.0)  # -> 7.0
    """

    def __init__(self, w: float, b: float) -> None:
        raise NotImplementedError

    def __call__(self, x: float) -> float:
        raise NotImplementedError


class TinyDataset:
    """Minimal indexable dataset supporting len(ds) and ds[i] (preview of PyTorch Dataset).

    Snapshot the input sequence so mutating the caller's list does not alter the dataset.
    """

    def __init__(self, items: Sequence[object]) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, idx: int) -> object:
        raise NotImplementedError


def batch_iter(items: Sequence[object], batch_size: int) -> Iterator[list[object]]:
    """Yield consecutive mini-batches (fresh lists) of up to `batch_size` items using `yield`.

    Example:
      list(batch_iter([1, 2, 3, 4, 5], 2)) -> [[1, 2], [3, 4], [5]]

    Raise ValueError if batch_size <= 0.
    """
    raise NotImplementedError
