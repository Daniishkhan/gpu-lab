import pytest

from vector_math import (
    cosine_similarity,
    dot_product,
    euclidean_distance,
    l1_norm,
    l2_norm,
    vec_add,
    vec_scale,
)


def test_add_and_scale():
    a = [1.0, -2.0, 3.0]
    b = [4.0, 5.0, -1.0]
    assert vec_add(a, b) == pytest.approx([5.0, 3.0, 2.0])
    assert vec_scale(a, 2.5) == pytest.approx([2.5, -5.0, 7.5])
    assert a == [1.0, -2.0, 3.0]  # no mutation

    with pytest.raises(ValueError):
        vec_add([], [])
    with pytest.raises(ValueError):
        vec_add([1.0], [1.0, 2.0])
    with pytest.raises(ValueError):
        vec_scale([], 2.0)


def test_norms_and_distance():
    assert l1_norm([3.0, -4.0]) == pytest.approx(7.0)
    assert l2_norm([3.0, -4.0]) == pytest.approx(5.0)
    assert euclidean_distance([1.0, 2.0], [4.0, 6.0]) == pytest.approx(5.0)
    assert euclidean_distance([2.0, 2.0], [2.0, 2.0]) == pytest.approx(0.0)

    with pytest.raises(ValueError):
        l1_norm([])
    with pytest.raises(ValueError):
        l2_norm([])
    with pytest.raises(ValueError):
        euclidean_distance([1.0], [1.0, 2.0])


def test_dot_product_and_cosine_similarity():
    assert dot_product([1.0, 2.0, 3.0], [4.0, -5.0, 6.0]) == pytest.approx(12.0)
    # Parallel, orthogonal, opposite, and scale-invariant checks
    assert cosine_similarity([1.0, 2.0], [10.0, 20.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 5.0]) == pytest.approx(0.0)
    assert cosine_similarity([2.0, -3.0], [-4.0, 6.0]) == pytest.approx(-1.0)

    with pytest.raises(ValueError):
        dot_product([], [])
    with pytest.raises(ValueError):
        cosine_similarity([0.0, 0.0], [1.0, 0.0])
    with pytest.raises(ValueError):
        cosine_similarity([1.0, 2.0], [1.0])
