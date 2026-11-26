---
name: run-gpu-lab
description: Cost-safe workflow for executing cloud GPU labs in gpu-labs/ on RunPod pods or SSH GPU VMs — enforces local CPU pre-flight checks, clean rsync/tmux execution, artifact capture, and mandatory pod teardown.
---

# Run a Cloud GPU Lab on RunPod or SSH VMs (`gpu/lab`)

Use this skill when the learner is ready to move from local CPU exercises (`exercises/`) onto real GPUs in **`gpu-labs/<NN>-<slug>/`** using **RunPod** or **SSH GPU VMs**.

> **Local-first rule:** During Phase 0A, Phase 0B, and Stage 1, everything runs 100% locally on CPU. Do not rent GPUs or build SSH automation until the learner reaches Stage 2+ (`gpu-labs/`).

## 1. Mandatory CPU Pre-Flight Gate (Before Spending $0.01)

Verify every item locally before connecting to a GPU pod:
1. All linked local CPU `pytest` exercises pass (`python3 -m pytest -k <modules>`).
2. Check VRAM & cost math in `book/workbench.html` and `book/reference-cheatsheet.html` — pick the cheapest GPU that fits cleanly (e.g., `1× L4 24GB` ~$0.70/hr, `1× L40S 48GB` ~$1.15/hr, `1× A100/H100 80GB`).
3. Confirm pinned library versions (`transformers>=5.10.1`, `peft>=0.19.0`, `trl>=0.16.0`, etc.) and required secrets (`HF_TOKEN` exported on the remote box, never committed to git).
4. For fine-tuning labs (Stage 3+): verify golden held-out `test.jsonl` and baseline greedy eval exist *before* starting training.

## 2. Clean Local-to-Remote Execution (RunPod & SSH VMs)

Keep the local Antigravity IDE as your source of truth so you never lose edits when an ephemeral RunPod pod terminates:
1. Use a clean `~/.ssh/config` host alias (e.g., `Host runpod-l4` or `Host gpu-vm`) so the exact same commands work for both RunPod SSH pods and dedicated SSH VMs.
2. Sync only the target lab directory (and datasets if small) with `rsync`:
   ```bash
   rsync -avz --exclude '.git' --exclude '.venv' --exclude 'scratch' --exclude '__pycache__' \
     gpu-labs/<NN>-<slug>/ <ssh-host>:~/gpu-lab/<NN>-<slug>/
   ```
3. Always run GPU jobs inside **`tmux`** (e.g. `tmux new -s lab`) so a dropped SSH connection never kills a training run mid-epoch.
4. Keep scripts self-contained with:
   - explicit CUDA warmup + `torch.cuda.synchronize()` before timing,
   - peak VRAM logging (`torch.cuda.max_memory_allocated() / 1e9`),
   - explicit stop tokens (`<turn|>` alongside `eos_token_id` for Gemma 4).

## 3. Monitor & Sanity-Check Early

- Watch `nvidia-smi` during the first 60 seconds to catch silent CPU fallback, unexpected OOM, or low utilization immediately.
- On fine-tuning runs, inspect 1 decoded sample with special tokens visible to verify `-100` completion-only masking before running a full epoch.
- Before serving behind `vLLM` / `SGLang`, run the mandatory `merge_and_unload()` greedy parity check on 10 held-out prompts.

## 4. Capture Artifacts & Mandatory Teardown

1. Push adapters, merged checkpoints, and eval JSON to Hugging Face Hub (or pull metrics/logs back locally) **before** stopping the pod.
2. Record measured VRAM, tok/s, eval deltas, and actual cost via:
   ```bash
   python3 tools/new.py exp "<Lab Run Title>"
   ```
   (writes to `journal/experiments/`).
3. **Explicit teardown check:** Confirm with the learner that the RunPod pod has been **stopped/terminated** (not left idling) as soon as artifacts are safely stored.
