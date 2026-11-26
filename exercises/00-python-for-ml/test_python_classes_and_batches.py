import inspect
import pytest

from python_classes_and_batches import LinearScaler, TinyDataset, Vec2D, batch_iter


def test_vec2d_dunders_and_no_mutation():
    a = Vec2D(1.0, 2.0)
    b = Vec2D(3.0, -4.0)
    c = a + b
    assert c == Vec2D(4.0, -2.0)
    assert (a * 3) == Vec2D(3.0, 6.0)
    # Original vectors stay unchanged
    assert a == Vec2D(1.0, 2.0)
    assert b == Vec2D(3.0, -4.0)
    assert repr(a).startswith("Vec2D(")


def test_linear_scaler_callable():
    layer = LinearScaler(w=2.5, b=-1.0)
    assert layer(4.0) == pytest.approx(9.0)
    assert layer(0.0) == pytest.approx(-1.0)


def test_tiny_dataset_len_getitem_and_copy():
    raw = ["apple", "banana", "cherry"]
    ds = TinyDataset(raw)
    raw.append("date")  # mutating caller list must not mutate TinyDataset
    assert len(ds) == 3
    assert ds[0] == "apple"
    assert ds[-1] == "cherry"


def test_batch_iter_generator():
    gen = batch_iter([10, 20, 30, 40, 50], 2)
    assert inspect.isgenerator(gen) or hasattr(gen, "__next__")
    assert list(gen) == [[10, 20], [30, 40], [50]]
    assert list(batch_iter([], 3)) == []
    with pytest.raises(ValueError):
        list(batch_iter([1, 2], 0))
    with pytest.raises(ValueError):
        list(batch_iter([1, 2], -1))
