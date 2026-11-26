"""LoRA math from scratch: parameter counts, forward pass, and exact merging.

Topic: 04.02

A LoRA adapter freezes a base weight matrix W (shape out_dim x in_dim) and
adds a low-rank bypass:

    y = W @ x + (alpha / r) * (B @ (A @ x))

where A has shape (r x in_dim) and B has shape (out_dim x r), with r << min(in_dim, out_dim).

At deployment time, merging bakes the adapter straight into W:

    W_merged = W + (alpha / r) * (B @ A)

so serving pays ZERO extra latency at inference!

Implement this in pure Python (no numpy/torch required) so every matrix
dimension and invariant is crystal clear in your head.

Say it out loud:
  1. Why is B initialized to zeros while A is initialized randomly? What breaks
     if both are zero, or if both are random?
  2. Why does merging LoRA into W cost zero extra FLOPs at serving time?
  3. When would you keep adapters unmerged (multi-LoRA serving) instead?
"""
from __future__ import annotations


def lora_param_count(in_dim: int, out_dim: int, rank: int) -> int:
    """Return total trainable parameters in A (rank x in_dim) and B (out_dim x rank).

    Raise ValueError if in_dim, out_dim, or rank <= 0.
    """
    raise NotImplementedError


def lora_forward(
    x: list[float],
    W: list[list[float]],
    A: list[list[float]],
    B: list[list[float]],
    alpha: float,
) -> list[float]:
    """Compute y = W @ x + (alpha / r) * (B @ (A @ x)).

    Shapes:
      x: len in_dim
      W: out_dim x in_dim
      A: r x in_dim
      B: out_dim x r

    Validate all shapes are non-empty, rectangular, and compatible; raise
    ValueError otherwise. Must not mutate inputs.
    """
    raise NotImplementedError


def merge_lora_weights(
    W: list[list[float]],
    A: list[list[float]],
    B: list[list[float]],
    alpha: float,
) -> list[list[float]]:
    """Return a NEW matrix W_merged = W + (alpha / r) * (B @ A).

    Validate all shapes are non-empty, rectangular, and compatible; raise
    ValueError otherwise. Must not mutate inputs.
    """
    raise NotImplementedError
