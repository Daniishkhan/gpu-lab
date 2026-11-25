---
name: review-chapter
description: Adversarially audit a gpu/lab chapter across four lenses (first-principles learner, Python-verified ML systems math, production gotchas, and offline/markup QA) and fix issues until clean.
---

# Adversarial Chapter Review (`gpu/lab`)

Act as a **ruthless editor** protecting the collective's quality bar. Assume there are subtle math errors, unintroduced jargon leaks, shallow analogies, or broken markup until you prove otherwise.

## Lens 1: First-Principles Learner (Zero Prior ML / Audio)

Check the chapter strictly against `curriculum.json`:
- **Prerequisite leaks:** Read the topic's `requires` list and spine position. Flag every concept, equation, or term used *before* it is introduced in an earlier stage or derived in this chapter.
- **Derivation vs. assertion:** Did the chapter *build* the idea via `Pain → Naive → Break → Toy Numbers → Visual → Formal Name`, or did it open with a textbook definition and ask the reader to take it on faith?
- **Running analogy discipline:** Is there ONE physical anchor carried through the chapter, AND does it explicitly state where the analogy breaks?
- **Core-path bloat:** Is the visible core path ~2,000–3,500 words? Move heavy proofs, alternative libraries, or edge-case tangents into collapsed `<details class="aside deeper">`.
- **Quick-check quality:** Are there 5–8 checks? Flag any trivia/recall question ("What does X stand for?") or obvious giveaway distractor. Every check must test a causal prediction or real bug, and `.fb.wrong` must explain from a second angle.
- **Anti-slop prose:** Flag patronizing words (*simply, obviously, trivially, just, easily, delve into*), wall-of-text paragraphs, and unworked skipped algebra.

## Lens 2: Skeptical ML Systems Engineer (Compute, Don't Eyeball!)

**Never verify arithmetic in your head.** Run `python3` to recompute:
- Every FLOP count, byte count, GB conversion (check `10^9` vs `2^30` consistency!), parameter count, KV-cache footprint, VRAM total, quantization rounding error, sample rate / Nyquist limit, and latency budget sum.
- Every pure-Python / NumPy code block shown in the chapter — execute it and confirm the output matches the prose and diagrams exactly.
- Every interactive JS widget formula in `<script>` — verify its math matches both the chapter prose and the matching CPU exercise in `sections/*/exercises/`.
- Every Gemma 4, PyTorch, TRL, PEFT, vLLM, SGLang, Qwen3-TTS, Chatterbox, Pipecat, LiveKit, or full-duplex S2S claim — cross-check against `reference-cheatsheet.html`, `labs/*.md`, and official docs when uncertain. Flag outdated APIs or unverified numbers.

## Lens 3: Production Builder (Real Gotchas & Boundaries)

Check whether the chapter exposes the real failure modes that burn teams in production — without bloating first-pass intuition:
- **Explicit "When NOT to use this" boundary:** Does the reader learn when prompting, RAG, a smaller model, or a cascade beats the technique in this chapter?
- **Domain-specific gotchas where relevant:**
  - Gemma 4: PLE total vs. effective params (`E2B`/`E4B`), MoE full-weight residency & frozen router (`26B-A4B`), NF4 degrading audio projections, `ClippableLinear` / `use_cache` pinned versions, ZeRO-3 empty-adapter bug, `-100` masking on turn/pad/audio soft tokens, mandatory `merge_and_unload()` greedy parity before vLLM/SGLang, official QAT checkpoints vs. PTQ.
  - Voice & telephony: 8 kHz G.711 μ-law 3.4 kHz cutoff, resampling mismatches (8k / 16k / 24k), spoken-register normalization, `<800 ms` end-to-end budget, `<200 ms` barge-in flush, and `text_spoken` vs. `text_remaining` reconciliation.
- **Zero exercise spoilers:** Confirm `#exercises` links cleanly to the local CPU exercise / GPU lab without leaking solution code.

## Lens 4: Automated Markup, Offline & Layout QA

Run all available automated checks — do not guess:
```bash
python3 tools/check_chapter.py <page.html>
python3 tools/build.py
```
And when Playwright is installed:
```bash
node tools/check_page.js <page.html>
```
Also verify manually:
- `<meta name="status" content="outline">` has been removed.
- Every `href` (prerequisites, `workbench.html`, exercises, `chapter-nav` prev/next) resolves to a real file on disk.
- All four themes stay readable (zero hardcoded hex/rgb colors in SVG or inline styles).

## Output Format & Fix Loop

Report findings grouped strictly by severity:
1. **Blocker (Wrong / Broken):** Incorrect math, wrong APIs, broken markup/links, external dependencies, leaked solutions, forward prerequisite violations.
2. **Clarity / First-Principles Gap:** Definition-first explanations, missing toy numbers, broken analogy, visual deserts, weak trivia checks, bloated main path.
3. **Missing Gotcha / Boundary:** Production failure mode or "when NOT to use" nuance that belongs in the chapter or a `details.aside.deeper`.
4. **Nits:** Minor wording, formatting, or polish.

Fix every item in **Blocker** and **Clarity / First-Principles Gap** (and worthwhile **Missing** items), then re-run `python3 tools/check_chapter.py <page.html>` and `python3 tools/build.py` until **Blocker** and **Clarity** are completely empty.
