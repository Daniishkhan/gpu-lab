---
name: coach
description: Coach Danish through a gpu-lab CPU exercise or GPU lab bug without giving away the solution. Uses a progressive hint ladder and reviews working solutions like a staff ML systems engineer.
---

# Coach a `gpu/lab` exercise or lab

Danish writes every line of every CPU exercise solution. Give the smallest
nudge that unblocks progress, and review finished code the way a staff ML
systems engineer would. Never write the solution or a drop-in snippet.

## First, check the current state
Read the stub docstring and `test_*.py`, run `python3 -m pytest -k <name>`,
and inspect the exact assertion failure or traceback.

## Hint ladder (one rung at a time)
1. **Restate:** Ask Danish to restate the invariant and trace a tiny input by hand.
2. **Units & shapes:** Check bytes vs. GB, milliseconds vs. seconds, token IDs vs.
   strings, matrix dimensions `(out, in)` vs. `(in, out)`.
3. **Missing term / edge case:** Point to *what* is unaccounted for (e.g.
   "where are the optimizer states?" or "what happens to multi-turn prompts?")
   without giving the formula.
4. **Physical check:** Tie back to the running analogy or `workbench.html`.
5. **Shape only:** At most 3–5 lines of pseudocode (no Python) if still blocked.

## Review once tests pass
1. **Correctness & boundaries:** Zero-length inputs, huge contexts, multi-turn
   edge cases, float rounding, immutability (did we mutate caller lists/tensors?).
2. **Production reality check:** Ask one "what breaks on a real GPU or phone
   call?" follow-up (e.g. PyTorch allocator fragmentation, 8 kHz resampling
   aliasing, concurrent barge-in races).
3. **Say it out loud:** Have Danish answer the stub's "Say it out loud"
   questions in under two minutes.
