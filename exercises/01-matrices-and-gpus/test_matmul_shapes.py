import pytest

from matmul_shapes import batched_linear, dot, matmul, transpose


def test_dot_product():
    assert dot([1.0, 2.0, 3.0], [4.0, -5.0, 6.0]) == pytest.approx(12.0)
    assert dot([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        dot([], [])
    with pytest.raises(ValueError):
        dot([1.0, 2.0], [1.0])


def test_transpose():
    m = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    snap = [r[:] for r in m]
    t = transpose(m)
    assert m == snap
    assert t == [[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]]
    with pytest.raises(ValueError):
        transpose([])
    with pytest.raises(ValueError):
        transpose([[1.0, 2.0], [3.0]])


def test_matmul_small_and_validation():
    A = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]          # (2, 3)
    B = [[7.0, 8.0], [9.0, 10.0], [11.0, 12.0]]     # (3, 2)
    C = matmul(A, B)
    assert C == [[58.0, 64.0], [139.0, 154.0]]
    with pytest.raises(ValueError):
        matmul(A, [[1.0, 2.0]])                     # 3 != 1
    with pytest.raises(ValueError):
        matmul([], B)


def test_batched_linear_llm_shape():
    # Batch B=2, sequence T=3 tokens, D_in=2 -> D_out=4
    x = [
        [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]],
        [[2.0, -1.0], [0.5, 0.5], [-1.0, 2.0]],
    ]
    W = [
        [1.0, 2.0, 0.0, -1.0],
        [0.0, 1.0, 3.0, 2.0],
    ]
    bias = [0.5, -0.5, 1.0, 0.0]
    out = batched_linear(x, W, bias)
    assert len(out) == 2 and len(out[0]) == 3 and len(out[0][0]) == 4
    assert out[0][0] == pytest.approx([1.5, 1.5, 1.0, -1.0])
    assert out[0][2] == pytest.approx([1.5, 2.5, 4.0, 1.0])
    assert out[1][0] == pytest.approx([2.5, 2.5, -2.0, -4.0])

    # Without bias
    out_nb = batched_linear(x, W)
    assert out_nb[0][0] == pytest.approx([1.0, 2.0, 0.0, -1.0])

    with pytest.raises(ValueError):
        batched_linear(x, W, bias=[0.0, 0.0])       # wrong bias length
    with pytest.raises(ValueError):
        batched_linear(x, [[1.0, 2.0]])             # D_in mismatch
