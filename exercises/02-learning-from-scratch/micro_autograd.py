"""Reverse-mode autograd & gradient descent from scratch (zero frameworks).

Topic: 02.01, 02.02

Build a tiny scalar autograd engine (inspired by Karpathy's micrograd) in pure
Python so `loss.backward()` in PyTorch is never magic again.

Requirements for Value:
  - Attributes: `data: float`, `grad: float` (initialized to 0.0)
  - Operations returning a new Value:
      `a + b`, `a - b`, `-a`, `a * b`, `a ** k` (k is int or float), `a.relu()`
    Support Python int/float on either side of `+`, `-`, `*` (e.g. `2.0 * x + 1`).
  - `backward()`:
      Builds a topological ordering of the computation graph ending at `self`,
      sets `self.grad = 1.0`, and walks backward accumulating (`+=`) local
      gradients into each parent's `.grad` (crucial when a node is used twice!).

Requirements for sgd_step(params, lr):
  - For every Value p in params: `p.data -= lr * p.grad`, then resets `p.grad = 0.0`.

Say it out loud:
  1. Why MUST backward() accumulate with `+=` instead of `=`? Give a 1-line example.
  2. Why do we walk the graph in reverse topological order instead of plain recursion?
  3. What goes wrong if you forget to zero `p.grad = 0.0` between training steps?
"""
from __future__ import annotations


class Value:
    """Scalar value that tracks its computation graph for reverse-mode backprop."""

    def __init__(self, data: float, _children: tuple[Value, ...] = ()) -> None:
        raise NotImplementedError

    def __add__(self, other: Value | int | float) -> Value:
        raise NotImplementedError

    def __radd__(self, other: int | float) -> Value:
        raise NotImplementedError

    def __neg__(self) -> Value:
        raise NotImplementedError

    def __sub__(self, other: Value | int | float) -> Value:
        raise NotImplementedError

    def __rsub__(self, other: int | float) -> Value:
        raise NotImplementedError

    def __mul__(self, other: Value | int | float) -> Value:
        raise NotImplementedError

    def __rmul__(self, other: int | float) -> Value:
        raise NotImplementedError

    def __pow__(self, exponent: int | float) -> Value:
        raise NotImplementedError

    def relu(self) -> Value:
        raise NotImplementedError

    def backward(self) -> None:
        raise NotImplementedError


def sgd_step(params: list[Value], lr: float) -> None:
    """Apply one gradient-descent step in-place and zero all gradients."""
    raise NotImplementedError
