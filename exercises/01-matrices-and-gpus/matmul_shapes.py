"""Vectors, matrix multiplication & batched linear layers from scratch.

Topic: 01.02

Every layer inside a Transformer (and Gemma 4) is built from one operation:
multiplying a batch of token vectors by a weight matrix. Build it once in pure
Python — tracing every dimension (B, T, D_in) @ (D_in, D_out) + bias — so
NumPy/PyTorch tensor shapes are never guesswork again.

Say it out loud:
  1. Geometrically, what does a large positive vs. zero vs. negative dot product tell you?
  2. Why does (B, T, D_in) @ (D_in, D_out) produce (B, T, D_out)?
  3. Why can a GPU compute every cell of A @ B on the exact same clock tick?
"""
from __future__ import annotations


def dot(a: list[float], b: list[float]) -> float:
    """Return sum(a[i] * b[i]). Raise ValueError if empty or lengths differ."""
    raise NotImplementedError


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    """Return a NEW transposed matrix of shape (C, R) from an (R, C) matrix.

    Raise ValueError if empty or ragged (rows have different lengths).
    Must not mutate input.
    """
    raise NotImplementedError


def matmul(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    """Multiply 2D matrices A (M, K) and B (K, N) -> NEW matrix (M, N).

    Raise ValueError if either matrix is empty, ragged, or inner dims differ.
    Must not mutate inputs.
    """
    raise NotImplementedError


def batched_linear(
    x: list[list[list[float]]],
    W: list[list[float]],
    bias: list[float] | None = None,
) -> list[list[list[float]]]:
    """Apply a neural linear projection to a 3D batch tensor x of shape (B, T, D_in):
        out[b][t] = (x[b][t] @ W) + bias   (for every batch item b and token t)

    Shapes:
      x:    (B, T, D_in)
      W:    (D_in, D_out)
      bias: optional (D_out,)
      returns: NEW 3D list of shape (B, T, D_out).

    Raise ValueError on empty, ragged, or incompatible shapes.
    Must not mutate inputs.
    """
    raise NotImplementedError
