"""GPU VRAM budgeting & cloud GPU picker for open-weight models.

Topic: 04.01

Before renting a cloud GPU (L4 24 GB, L40S 48 GB, H100 80 GB), compute exact
memory footprints in decimal gigabytes (1 GB = 10**9 bytes) so an OOM never
surprises you on step 1.

Precision byte multipliers (weight_memory_gb):
  - "fp32"         -> 4.0 bytes/param
  - "bf16", "fp16" -> 2.0 bytes/param
  - "fp8", "int8"  -> 1.0 bytes/param
  - "q4", "nf4"    -> 0.55 bytes/param (includes quantization scale metadata)

Training modes (training_memory_gb):
  - "qlora":     4-bit frozen base (0.55 B/p) + grads (2 B) & 8-bit opt (2 B)
                 ONLY on trainable_fraction of params
  - "bf16_lora": BF16 frozen base (2.0 B/p) + grads (2 B) & 8-bit opt (2 B)
                 ONLY on trainable_fraction of params
  - "full_8bit": BF16 weights (2.0 B/p) + BF16 grads (2.0 B/p) + 8-bit AdamW (2.0 B/p)
                 on 100% of params
  - "full_fp32": BF16 weights (2.0 B/p) + BF16 grads (2.0 B/p) + FP32 AdamW (8.0 B/p)
                 on 100% of params

Say it out loud:
  1. Why does BF16 LoRA cut ~50 GB off Gemma 4 12B compared to full fine-tuning
     even though the base weights are still 16-bit?
  2. When serving 16 concurrent callers, which term scales 16x and which stays 1x?
  3. Why should you prefer BF16 LoRA over NF4 QLoRA for Gemma 4 audio fine-tuning?
"""
from __future__ import annotations


def weight_memory_gb(total_params_b: float, precision: str) -> float:
    """Return static weight footprint in decimal GB (1e9 bytes).

    Raise ValueError if total_params_b <= 0 or precision is unknown.
    """
    raise NotImplementedError


def kv_cache_gb(
    num_layers: int,
    num_kv_heads: int,
    head_dim: int,
    seq_len: int,
    concurrency: int,
    bytes_per_elem: int = 2,
) -> float:
    """Return total KV-cache memory in decimal GB (1e9 bytes) for active requests.

    Formula: 2 (K and V) * num_layers * num_kv_heads * head_dim
             * bytes_per_elem * seq_len * concurrency / 1e9.
    Raise ValueError if any argument is <= 0.
    """
    raise NotImplementedError


def training_memory_gb(
    total_params_b: float,
    mode: str,
    trainable_fraction: float = 0.015,
    activation_gb: float = 2.5,
    overhead_gb: float = 1.5,
) -> dict[str, float]:
    """Return a dict with keys:
      'weights_gb', 'gradients_gb', 'optimizer_gb',
      'activation_gb', 'overhead_gb', 'total_gb'.

    Raise ValueError for unknown mode, total_params_b <= 0,
    or trainable_fraction not in (0, 1].
    """
    raise NotImplementedError


def pick_cheapest_gpu(
    required_gb: float,
    catalog: list[tuple[str, float, float]],
    headroom_ratio: float = 0.10,
) -> str:
    """Pick the cheapest GPU name from catalog [(name, vram_gb, hourly_usd), ...]
    that satisfies vram_gb >= required_gb * (1 + headroom_ratio).

    Tie-break equal hourly_usd by smaller vram_gb, then alphabetically by name.
    Raise ValueError if required_gb <= 0, headroom_ratio < 0, or no GPU fits.
    """
    raise NotImplementedError
