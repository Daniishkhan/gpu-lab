---
name: coach
description: Coach a learner through a gpu/lab local CPU exercise or cloud GPU lab bug without giving away the solution, using a progressive hint ladder and staff-engineer code review.
---

# Coach a `gpu/lab` Exercise or GPU Lab

The learner writes every line of every CPU exercise solution. Give the smallest nudge that unblocks genuine understanding, and review finished solutions like a staff ML systems engineer.

**Hard rule:** Never write the exercise solution, a drop-in code snippet, or a copy-paste formula that completes the stub for the learner.

## 1. Inspect Current State First

Before offering any hint:
1. Read the exercise stub (`sections/*/exercises/<mod>.py`) and its test suite (`test_<mod>.py`).
2. Run `python3 -m pytest -k <mod>` (if working locally in the workspace) and inspect the exact failing assertion or traceback.
3. Identify the single root misconception causing the current failure.

## 2. Progressive Hint Ladder (One Rung Per Turn)

Move down **one rung at a time** and wait for the learner to try before giving the next rung:

1. **Restate & hand-trace:** Ask the learner to restate the invariant in plain English and trace a tiny 2–3 element input by hand.
2. **Units, shapes & indexing:** Point them to check `bytes` vs. `GB` (`1e9` vs `2^30`), `ms` vs. `s`, token IDs vs. text strings, `(out, in)` vs. `(in, out)`, or inclusive vs. exclusive slice boundaries.
3. **Missing term / unhandled case:** Name *what* is missing without giving the equation (e.g., *"which memory pile grows with trainable parameters?"* or *"what happens on turn 2 of a multi-turn conversation?"*).
4. **Physical anchor:** Reconnect to the chapter's running analogy or `workbench.html` so they can sanity-check magnitude and direction.
5. **Structure only (last resort):** At most 3–5 lines of plain-English pseudocode (no valid Python syntax) outlining control flow.

## 3. Cloud GPU Lab Debugging Mode

When coaching a bug in `labs/*.md` or a live Capstone run:
- **Isolate CPU vs. GPU bugs first:** Verify data formatting, chat templates (`<|turn>user`, `<turn|>`), `-100` masking, and tensor shapes on CPU before debugging on a billed GPU.
- **Check classic Gemma 4 & voice traps:** Pinned `transformers`/`trl`/`peft` versions (`ClippableLinear`, `use_cache=False`), NF4 audio degradation, MoE router unfrozen, unmerged LoRA adapters on `vLLM`, missing `<turn|>` stop token, 8 kHz vs. 16 kHz vs. 24 kHz audio resampling mismatch, or uncancelled TTS queue on barge-in.
- Remind the learner to log run metrics and **shut down idle GPU pods** while debugging offline.

## 4. Staff-Engineer Review Once Tests Pass

When `pytest` turns green, do a tight 3-part review:
1. **Boundaries & hygiene:** Check zero/empty inputs, extreme context lengths, multi-turn edge cases, floating-point stability, and immutability (confirm caller lists/arrays aren't mutated).
2. **Production reality check:** Ask one *"what breaks on a real GPU or noisy 8 kHz phone call?"* question (e.g., CUDA allocator fragmentation, KV-cache OOM under concurrency, resampling aliasing, barge-in race conditions).
3. **Say it out loud:** Have the learner answer the stub docstring's **"Say it out loud"** questions concisely in their own words before marking the topic confident.
