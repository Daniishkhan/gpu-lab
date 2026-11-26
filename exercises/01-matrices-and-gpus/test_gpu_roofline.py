import pytest

from gpu_roofline import (
    classify_workload,
    decode_upper_bound_tok_s,
    matmul_flops,
    ridge_point_flops_per_byte,
)


def test_matmul_flops():
    # Single 4096x4096 layer on 4096 tokens -> 137,438,953,472 FLOPs
    assert matmul_flops(4096, 4096, 4096) == 2 * 4096 * 4096 * 4096
    assert matmul_flops(1, 3, 2) == 12
    with pytest.raises(ValueError):
        matmul_flops(0, 4, 4)


def test_ridge_point_l4_and_h100():
    # NVIDIA L4: 121 TFLOPS BF16, 300 GB/s -> 403.33 FLOPs/byte
    assert ridge_point_flops_per_byte(121.0, 300.0) == pytest.approx(403.333333, rel=1e-4)
    # NVIDIA H100: 989 TFLOPS BF16, 3350 GB/s -> 295.22 FLOPs/byte
    assert ridge_point_flops_per_byte(989.0, 3350.0) == pytest.approx(295.22388, rel=1e-4)
    with pytest.raises(ValueError):
        ridge_point_flops_per_byte(-10.0, 300.0)


def test_decode_upper_bound_and_quantization_speedup():
    # Gemma 4 12B BF16 (24 GB) on L4 (300 GB/s) -> 12.5 tok/s physical ceiling
    bf16 = decode_upper_bound_tok_s(12.0, 2.0, 300.0)
    assert bf16 == pytest.approx(12.5)
    # 4-bit (~0.5 B/p) -> 4x faster ceiling!
    q4 = decode_upper_bound_tok_s(12.0, 0.5, 300.0)
    assert q4 == pytest.approx(50.0)
    # MoE 26B-A4B (4B active in BF16 = 8 GB read) on H100 (3350 GB/s) -> ~418.75 tok/s
    moe = decode_upper_bound_tok_s(4.0, 2.0, 3350.0)
    assert moe == pytest.approx(418.75)


def test_classify_decode_vs_prefill():
    # Single-user decode of 12B BF16 on L4: 1 FLOP/byte << 403.33 ridge -> memory_bound!
    dec = classify_workload(12.0, 2.0, batch_tokens=1, peak_tflops=121.0, mem_bw_gb_s=300.0)
    assert dec["regime"] == "memory_bound"
    assert dec["arithmetic_intensity"] == pytest.approx(1.0)
    assert dec["memory_ms"] == pytest.approx(80.0)
    assert dec["compute_utilization"] < 0.01

    # 1,024-token prefill of 12B BF16 on L4: 1024 FLOPs/byte >> 403.33 ridge -> compute_bound!
    pre = classify_workload(12.0, 2.0, batch_tokens=1024, peak_tflops=121.0, mem_bw_gb_s=300.0)
    assert pre["regime"] == "compute_bound"
    assert pre["arithmetic_intensity"] == pytest.approx(1024.0)
    assert pre["compute_utilization"] == pytest.approx(1.0)

    with pytest.raises(ValueError):
        classify_workload(12.0, 2.0, batch_tokens=0, peak_tflops=121.0, mem_bw_gb_s=300.0)
