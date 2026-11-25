---
name: author-exercise
description: Design and verify a zero-GPU pure-Python/NumPy first-principles CPU exercise stub and adversarial pytest suite for gpu/lab, verified via tools/check_exercise.py without committing solutions.
---

# Author a Zero-GPU First-Principles Exercise (`gpu/lab`)

Every CPU exercise in `sections/<NN>/exercises/` proves **one concrete engineering invariant** locally in pure Python or NumPy (zero GPU, zero cloud spend, zero external downloads) before a learner ever imports a high-level wrapper or rents a GPU pod.

## 1. Ground & Scaffold

1. Read `curriculum.json` and the matching chapter (`sections/<NN>/concepts/*.html`) so function names, units (`bytes` vs `GB`, `ms` vs `s`), tensor shapes, and mental models match the chapter 1-to-1.
2. Pick a **repo-wide unique module name** (no `__init__.py` exists under `sections/`).
3. Scaffold with:
   ```bash
   python3 tools/new.py exercise <TOPIC_ID> <module_name> "<Concise Title>"
   ```

## 2. Stub Design Contract (`sections/<NN>/exercises/<module>.py`)

- **Header docstring:** Include `Topic: XX.YY` (or `Topic: XX.YY, XX.ZZ` if spanning two topics — `tools/build.py` parses this line!), a plain-English description of the physical/engineering invariant being verified, and a **"Say it out loud:"** block with 2–4 conceptual prediction questions.
- **Small, composable functions (3–5 functions):** Progress from the atomic primitive (e.g., `dot_product`, `matmul_flops`, `mask_single_turn`) up to the real systems calculation (e.g., `batched_linear`, `classify_workload`, `mask_conversation`).
- **Explicit contracts:** Every function docstring must state:
  - exact parameter types and shapes (e.g., `(B, T, D_in)`),
  - exact units (`1e9` decimal GB vs `1024**3` GiB — be explicit!),
  - exact return structure (dict keys, tolerance expectations, immutability),
  - exact `ValueError` conditions (e.g., dimensions `<= 0`, mismatched inner shapes, empty inputs).
- **Hard no-solution rule:** Every function body in the repo stub **must** raise `NotImplementedError`. Never leave commented-out solution code or drop-in snippets in the stub.

## 3. Adversarial Test Suite (`sections/<NN>/exercises/test_<module>.py`)

Design `test_<module>.py` so a passing implementation is genuinely right — not just lucky on one happy path:
1. **Hand-traceable tiny cases:** 2–4 element inputs whose expected outputs a learner can verify on paper in 30 seconds.
2. **Core mathematical & physical invariants:** E.g., finite-difference gradient checks for autograd, LoRA `B = 0` zero-init invariance, exact `W_merged == W + (alpha/r) * (B @ A)` parity, `-100` masking on system/user/pad/audio tokens, causal mask future-blindness, KV-cache equivalence with uncached forward pass.
3. **Real production specs:** At least one test grounded in real hardware/model numbers (e.g., L4 vs. H100 ridge point, Gemma 4 E4B/12B/26B-A4B VRAM, `<800 ms` voice pipeline & `<200 ms` barge-in).
4. **Edge cases & safety:** Boundary inputs, `pytest.raises(ValueError)` on bad shapes/units, and **immutability checks** verifying the learner didn't mutate caller-owned lists or arrays.
5. **Fast & offline:** Entire module test file runs in `< 1 s` on CPU using only stdlib + `numpy` + `pytest`.

## 4. Mandatory Out-of-Repo Verification

Never put reference solutions inside the repo. Verify your tests prove what they claim using a temporary scratch directory *outside* the repo:

1. Create `/tmp/gpu-lab-check-<module>/ref.py` (clean passing reference) and at least one `/tmp/gpu-lab-check-<module>/bad_*.py` (subtly wrong implementation — e.g., off-by-one mask, missing `alpha/r` scaling, wrong dimension validation, mutating input).
2. Run:
   ```bash
   python3 tools/check_exercise.py <module> \
     --pass /tmp/gpu-lab-check-<module>/ref.py \
     --fail /tmp/gpu-lab-check-<module>/bad_1.py
   ```
3. Confirm:
   - The repo stub **fails** with `NotImplementedError`.
   - Every `--pass` reference **passes** 100%.
   - Every `--fail` buggy implementation **fails** at least one test.
4. **Delete** `/tmp/gpu-lab-check-<module>/` immediately afterward.
5. Run `python3 tools/build.py` and verify the new exercise appears cleanly on the subject page and in `assets/curriculum.js`.
