---
name: write-lab
description: Author or update a reproducible cloud GPU lab runbook in gpu-labs/<NN>-<slug>/README.md with CPU pre-flight checks, pinned versions, VRAM/cost estimates, production gotchas, and pod teardown steps.
---

# Write a Cloud GPU Lab Runbook (`gpu/lab`)

Cloud GPU labs in `gpu-labs/<NN>-<slug>/README.md` bridge the gap between local CPU toy builds and real open-weight systems without burning money on trivial bugs. Every runbook must be reproducible, cost-aware, and tied directly back to first-principles predictions from the book.

## 1. Ground & Scaffold

1. Check `curriculum.json`, `gpu-labs/README.md`, and `book/reference-cheatsheet.html` for the target stage, topic ID(s), linked CPU exercises, and canonical GPU sizing.
2. Scaffold with `python3 tools/new.py runbook "<Runbook Title>"` (or create the next numbered `gpu-labs/<NN>-<slug>/README.md` for a core spine lab and register it in `gpu-labs/README.md` + `curriculum.json`).

## 2. Mandatory Runbook Structure

Every runbook must contain these six sections:

1. **Header Metadata:**
   - **Topic & Stage:** exact topic ID(s) and Capstone link.
   - **Recommended GPU:** cheapest GPU that fits cleanly (e.g., `1× NVIDIA L4 24GB`, `1× L40S 48GB`, `1× A100/H100 80GB`) with cloud provider examples (RunPod, Modal, Lambda, Colab Pro).
   - **Estimated VRAM / Runtime / Cost:** explicit realistic numbers (never leave blank).
2. **Pre-Flight Checks (CPU-Only, Before Renting):**
   - Exact chapter(s) to read and exact `python3 -m pytest -k ...` CPU exercise(s) to pass locally first.
   - Required dataset files, golden held-out eval baseline measured *before* training, tokens (`HF_TOKEN`), or consented audio clips.
3. **Environment Setup (Pinned Versions):**
   - Pin minimum known-good versions for Gemma 4 / voice stack (e.g., `transformers>=5.10.1`, `trl>=0.16.0`, `peft>=0.19.0`, `accelerate>=1.4.0` — verify against `reference-cheatsheet.html` and current official docs).
   - Never rely on floating unpinned installs that silently break on `ClippableLinear`, `use_cache`, or audio processors.
4. **Runnable Minimal Script / Commands:**
   - Clean, self-contained code or CLI commands with explicit warmup (`torch.cuda.synchronize()` before timing), stop tokens (`<turn|>`), and peak VRAM / latency printing.
   - Expose the **2–4 production gotchas** baked into the recipe (e.g., BF16 LoRA vs. NF4 for audio, `-100` completion-only masking, avoiding DeepSpeed ZeRO-3 with LoRA, mandatory `merge_and_unload()` greedy parity check before `vLLM`/`SGLang`, 8 kHz μ-law `ffmpeg` round-trip check for voice).
5. **First-Principles Observation & Experiment Tasks:**
   - Give 2–4 concrete experiments that tie real hardware behavior back to theory: e.g., *"Compare measured peak VRAM against your `vram_budget.py` prediction"*, *"Remove `<turn|>` from `eos_token_id` once and observe what happens"*, *"Compare 24 kHz studio vs. 8 kHz μ-law round-trip WER"*.
6. **Artifacts & Teardown Checklist:**
   - Push adapters, merged weights, audio samples, and eval JSON to Hugging Face Hub or cloud storage **before** terminating the pod.
   - Log baseline vs. run deltas in `workbench.html` or `tools/new.py exp`.
   - Explicit reminder to shut down the GPU pod immediately once done.

## 3. Quality Gate

- Verify all arithmetic (VRAM estimates, runtime × hourly rate = cost, sample rates, latency targets) using `python3`.
- Cross-check all model IDs, special tokens, and library flags against `book/reference-cheatsheet.html` and official docs.
- Confirm `gpu-labs/README.md` lists the runbook if it is part of the main sequence.
