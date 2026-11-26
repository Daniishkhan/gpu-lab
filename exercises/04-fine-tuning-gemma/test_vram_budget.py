import pytest

from vram_budget import (
    kv_cache_gb,
    pick_cheapest_gpu,
    training_memory_gb,
    weight_memory_gb,
)


def test_weight_memory_precisions():
    assert weight_memory_gb(12.0, "bf16") == pytest.approx(24.0)
    assert weight_memory_gb(12.0, "fp16") == pytest.approx(24.0)
    assert weight_memory_gb(12.0, "fp8") == pytest.approx(12.0)
    assert weight_memory_gb(12.0, "int8") == pytest.approx(12.0)
    assert weight_memory_gb(12.0, "q4") == pytest.approx(6.6)
    assert weight_memory_gb(12.0, "nf4") == pytest.approx(6.6)
    assert weight_memory_gb(12.0, "fp32") == pytest.approx(48.0)


def test_weight_memory_validation():
    with pytest.raises(ValueError):
        weight_memory_gb(0, "bf16")
    with pytest.raises(ValueError):
        weight_memory_gb(-4.0, "bf16")
    with pytest.raises(ValueError):
        weight_memory_gb(12.0, "int3")


def test_kv_cache_linear_scaling():
    # 32 layers, 8 KV heads, 128 head_dim, BF16 (2 bytes)
    one_user_4k = kv_cache_gb(32, 8, 128, seq_len=4096, concurrency=1)
    # 2 * 32 * 8 * 128 * 2 * 4096 / 1e9 = 0.536870912 GB
    assert one_user_4k == pytest.approx(0.536870912, rel=1e-6)
    sixteen_users = kv_cache_gb(32, 8, 128, seq_len=4096, concurrency=16)
    assert sixteen_users == pytest.approx(16 * one_user_4k, rel=1e-6)
    fp8_kv = kv_cache_gb(32, 8, 128, seq_len=4096, concurrency=1, bytes_per_elem=1)
    assert fp8_kv == pytest.approx(one_user_4k / 2, rel=1e-6)


def test_kv_cache_validation():
    with pytest.raises(ValueError):
        kv_cache_gb(32, 8, 128, seq_len=0, concurrency=1)
    with pytest.raises(ValueError):
        kv_cache_gb(32, 8, 128, seq_len=1024, concurrency=0)


def test_training_memory_modes_gemma_12b():
    qlora = training_memory_gb(12.0, "qlora", trainable_fraction=0.015, activation_gb=2.5, overhead_gb=1.5)
    assert qlora["weights_gb"] == pytest.approx(6.6)
    assert qlora["gradients_gb"] == pytest.approx(12.0 * 0.015 * 2.0)
    assert qlora["optimizer_gb"] == pytest.approx(12.0 * 0.015 * 2.0)
    assert qlora["total_gb"] == pytest.approx(6.6 + 0.36 + 0.36 + 2.5 + 1.5)

    bf16_lora = training_memory_gb(12.0, "bf16_lora", trainable_fraction=0.015, activation_gb=3.0, overhead_gb=1.5)
    assert bf16_lora["weights_gb"] == pytest.approx(24.0)
    assert bf16_lora["gradients_gb"] == pytest.approx(0.36)
    assert bf16_lora["optimizer_gb"] == pytest.approx(0.36)

    full8 = training_memory_gb(12.0, "full_8bit", activation_gb=5.0, overhead_gb=3.0)
    assert full8["weights_gb"] == pytest.approx(24.0)
    assert full8["gradients_gb"] == pytest.approx(24.0)
    assert full8["optimizer_gb"] == pytest.approx(24.0)
    assert full8["total_gb"] == pytest.approx(80.0)

    full32 = training_memory_gb(12.0, "full_fp32", activation_gb=5.0, overhead_gb=3.0)
    assert full32["optimizer_gb"] == pytest.approx(96.0)
    assert full32["total_gb"] == pytest.approx(152.0)

    assert qlora["total_gb"] < bf16_lora["total_gb"] < full8["total_gb"] < full32["total_gb"]


def test_training_memory_validation():
    with pytest.raises(ValueError):
        training_memory_gb(12.0, "magic_mode")
    with pytest.raises(ValueError):
        training_memory_gb(12.0, "qlora", trainable_fraction=0.0)
    with pytest.raises(ValueError):
        training_memory_gb(12.0, "qlora", trainable_fraction=1.5)


def test_pick_cheapest_gpu():
    catalog = [
        ("H100-80GB", 80.0, 2.90),
        ("L4-24GB", 24.0, 0.70),
        ("L40S-48GB", 48.0, 1.15),
        ("A100-80GB", 80.0, 1.85),
    ]
    # 11 GB * 1.10 = 12.1 GB -> L4 fits cheaply
    assert pick_cheapest_gpu(11.0, catalog) == "L4-24GB"
    # 22.5 GB * 1.10 = 24.75 GB -> L4 too tight, must pick L40S
    assert pick_cheapest_gpu(22.5, catalog) == "L40S-48GB"
    # 70 GB * 1.10 = 77 GB -> A100 beats H100 on cost
    assert pick_cheapest_gpu(70.0, catalog) == "A100-80GB"

    # Tie-breaker: same hourly rate -> smaller VRAM first, then alphabetical
    tied = [("GPU-B", 48.0, 1.00), ("GPU-A", 24.0, 1.00), ("GPU-C", 24.0, 1.00)]
    assert pick_cheapest_gpu(10.0, tied) == "GPU-A"

    with pytest.raises(ValueError):
        pick_cheapest_gpu(90.0, catalog)
