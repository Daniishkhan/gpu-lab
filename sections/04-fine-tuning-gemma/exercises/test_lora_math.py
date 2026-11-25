import random
import pytest

from lora_math import lora_forward, lora_param_count, merge_lora_weights


def _matvec(M, x):
    return [sum(row[j] * x[j] for j in range(len(x))) for row in M]


def test_lora_param_count():
    # A 4096 x 4096 projection has 16.77M weights; r=16 LoRA has only 131,072 (<0.8%)
    assert lora_param_count(4096, 4096, 16) == 131_072
    assert lora_param_count(3072, 1024, 32) == 32 * (3072 + 1024)
    with pytest.raises(ValueError):
        lora_param_count(0, 64, 8)
    with pytest.raises(ValueError):
        lora_param_count(64, 64, 0)


def test_zero_init_invariant():
    """When B is all zeros, LoRA forward MUST match the untouched base model."""
    W = [[1.0, 2.0, -1.0], [0.5, -0.5, 3.0]]
    A = [[0.7, -0.3, 0.2], [0.1, 0.9, -0.4]]
    B_zero = [[0.0, 0.0], [0.0, 0.0]]
    x = [2.0, -1.0, 4.0]
    assert lora_forward(x, W, A, B_zero, alpha=4.0) == pytest.approx(_matvec(W, x))


def test_forward_and_merge_exact_equivalence():
    """Merged weights W_merged @ x MUST match unmerged lora_forward(x) to machine precision."""
    rng = random.Random(42)
    for in_dim, out_dim, r, alpha in [(3, 2, 1, 2.0), (8, 5, 2, 4.0), (12, 10, 4, 8.0)]:
        W = [[rng.uniform(-1, 1) for _ in range(in_dim)] for _ in range(out_dim)]
        A = [[rng.uniform(-1, 1) for _ in range(in_dim)] for _ in range(r)]
        B = [[rng.uniform(-1, 1) for _ in range(r)] for _ in range(out_dim)]
        x = [rng.uniform(-2, 2) for _ in range(in_dim)]
        W_copy = [row[:] for row in W]

        y_unmerged = lora_forward(x, W, A, B, alpha)
        W_merged = merge_lora_weights(W, A, B, alpha)
        assert W == W_copy, "W must not be mutated"
        y_merged = _matvec(W_merged, x)
        assert y_merged == pytest.approx(y_unmerged, abs=1e-9)


def test_shape_mismatch_raises():
    W = [[1.0, 2.0], [3.0, 4.0]]
    A_bad = [[1.0, 2.0, 3.0]]  # wrong in_dim
    B_ok = [[1.0], [2.0]]
    with pytest.raises(ValueError):
        lora_forward([1.0, 2.0], W, A_bad, B_ok, alpha=2.0)
    with pytest.raises(ValueError):
        merge_lora_weights(W, A_bad, B_ok, alpha=2.0)
    with pytest.raises(ValueError):
        lora_forward([1.0], W, [[1.0, 2.0]], B_ok, alpha=2.0)
