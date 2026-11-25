"""GPU roofline math: FLOPs, VRAM bandwidth, arithmetic intensity & decode speed.

Topic: 01.03

Every GPU has two speed walls:
  1. Peak compute (TFLOPS = 10^12 FLOPs/sec)
  2. VRAM memory bandwidth (GB/s = 10^9 bytes/sec)

Compute the exact crossover (ridge point), single-user decode speed ceiling,
and classify whether a batched LLM step is memory-bandwidth-bound or compute-bound.

Say it out loud:
  1. Why is single-user LLM generation almost always memory-bandwidth-bound?
  2. Why does 4-bit quantization speed up single-user decode by ~3-4x?
  3. Why can continuous batching serve 8 callers in nearly the same step time as 1?
"""
from __future__ import annotations


def matmul_flops(m: int, k: int, n: int) -> int:
    """Return total floating-point ops (multiplies + adds) for (m, k) @ (k, n): 2 * m * k * n.

    Raise ValueError if any dimension <= 0.
    """
    raise NotImplementedError


def ridge_point_flops_per_byte(peak_tflops: float, mem_bw_gb_s: float) -> float:
    """Return the GPU ridge point in FLOPs/byte: (peak_tflops * 1e12) / (mem_bw_gb_s * 1e9).

    Raise ValueError if peak_tflops <= 0 or mem_bw_gb_s <= 0.
    """
    raise NotImplementedError


def decode_upper_bound_tok_s(
    active_params_b: float,
    bytes_per_param: float,
    mem_bw_gb_s: float,
) -> float:
    """Return physical max single-user decode tokens/sec limited by reading active weights:
        mem_bw_gb_s / (active_params_b * bytes_per_param).

    Raise ValueError if any argument <= 0.
    """
    raise NotImplementedError


def classify_workload(
    active_params_b: float,
    bytes_per_param: float,
    batch_tokens: int,
    peak_tflops: float,
    mem_bw_gb_s: float,
) -> dict[str, object]:
    """Model one forward step reading active_params_b weights once across batch_tokens:
      - flops = 2 * active_params_b * 1e9 * batch_tokens
      - bytes_moved = active_params_b * bytes_per_param * 1e9
      - arithmetic_intensity = flops / bytes_moved
      - ridge_point = ridge_point_flops_per_byte(peak_tflops, mem_bw_gb_s)
      - compute_ms = (flops / (peak_tflops * 1e12)) * 1000.0
      - memory_ms = (bytes_moved / (mem_bw_gb_s * 1e9)) * 1000.0
      - step_ms = max(compute_ms, memory_ms)
      - compute_utilization = min(1.0, compute_ms / step_ms)
      - regime = "memory_bound" if arithmetic_intensity < ridge_point else "compute_bound"

    Return a dict with keys:
      'arithmetic_intensity', 'ridge_point', 'compute_ms', 'memory_ms',
      'step_ms', 'compute_utilization', 'regime'.
    Raise ValueError if any input <= 0.
    """
    raise NotImplementedError
