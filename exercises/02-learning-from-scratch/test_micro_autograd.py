import pytest

from micro_autograd import Value, sgd_step


def test_chain_rule_matches_finite_difference():
    def expr(a_val, b_val):
        a = Value(a_val)
        b = Value(b_val)
        c = (a * b + a ** 2 - 3.0 * b + 1.5).relu()
        out = c * 2.0 + b ** 3
        return a, b, out

    a, b, out = expr(2.0, -1.5)
    out.backward()

    h = 1e-6
    _, _, out_ap = expr(2.0 + h, -1.5)
    _, _, out_am = expr(2.0 - h, -1.5)
    _, _, out_bp = expr(2.0, -1.5 + h)
    _, _, out_bm = expr(2.0, -1.5 - h)
    assert a.grad == pytest.approx((out_ap.data - out_am.data) / (2 * h), rel=1e-4)
    assert b.grad == pytest.approx((out_bp.data - out_bm.data) / (2 * h), rel=1e-4)


def test_shared_node_accumulates_gradients():
    """Using the same Value multiple times must accumulate (+=) instead of overwriting."""
    x = Value(3.0)
    y = x + x + x * x  # dy/dx = 1 + 1 + 2x = 8
    y.backward()
    assert y.data == pytest.approx(15.0)
    assert x.grad == pytest.approx(8.0)


def test_relu_blocks_negative_gradients():
    x = Value(-2.5)
    y = x.relu()
    y.backward()
    assert y.data == 0.0
    assert x.grad == 0.0

    z = Value(4.0)
    w = (2.0 * z).relu()
    w.backward()
    assert w.data == 8.0
    assert z.grad == 2.0


def test_fit_toy_line_via_gradient_descent():
    """Fit y = 3*x - 1 from 4 points purely with our from-scratch Value + sgd_step."""
    data = [(0.0, -1.0), (1.0, 2.0), (2.0, 5.0), (3.0, 8.0)]
    w = Value(0.0)
    b = Value(0.0)

    for _ in range(150):
        loss = Value(0.0)
        for x, y_true in data:
            pred = w * x + b
            loss = loss + (pred - y_true) ** 2
        loss = loss * (1.0 / len(data))
        loss.backward()
        sgd_step([w, b], lr=0.08)

    assert w.grad == 0.0 and b.grad == 0.0
    assert w.data == pytest.approx(3.0, abs=1e-2)
    assert b.data == pytest.approx(-1.0, abs=1e-2)
