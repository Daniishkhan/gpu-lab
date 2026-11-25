---
name: review-chapter
description: Adversarially review a gpu-lab chapter for inaccurate ML/hardware numbers, confusing explanations, missing production gotchas, or weak quick checks and tests.
---

# Review a `gpu/lab` chapter adversarially

Read the chapter three ways:
1. **As a sharp SWE new to PyTorch & fine-tuning:** flag unintroduced jargon,
   missing analogies, visual deserts, dry textbook openers, or bloated main
   paths that should be in `details.aside.deeper`.
2. **As a skeptical ML systems engineer:** recompute EVERY VRAM byte count,
   parameter count, latency sum, sample rate, and Gemma 4 / TTS / telephony
   claim. Verify code snippets match current APIs (`transformers>=5.10.1`,
   `trl>=0.16.0`, `peft>=0.19.0`, `vLLM`, `Pipecat`).
3. **As a production builder:** check whether the chapter exposes real gotchas
   (`gemma.ai` gaps: NF4 on audio, MoE router collapse, `-100` masking,
   vLLM adapter merging, 8 kHz μ-law telephony loss, barge-in state leaks)
   without bloating first-pass intuition.

Report findings grouped by **Wrong**, **Unclear / Too Complex**, **Missing**,
and **Nits**, fix them, and re-verify until **Wrong** and **Unclear** are empty.
