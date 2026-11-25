---
name: write-chapter
description: Author or rewrite a gpu/lab visual HTML book chapter from first principles for the collective, using worked small-number derivations, one running physical analogy, prediction quick checks, and production gotchas.
---

# Write a First-Principles `gpu/lab` Chapter

Write a chapter that reads like one cohesive, unforgettable book for our collective: after a single top-to-bottom read, any engineer with basic Python fluency **derives** why the mechanism exists, holds a clear visual mental model, spots the real production gotchas missing from vendor docs, and is ready to code the local CPU exercise or run the cloud GPU lab.

Before writing any HTML, read [`references/html-components.md`](references/html-components.md) for the exact CSS classes, JS widgets, and offline markup contract.

## Phase 1: Grounding & Prerequisite Audit (Mandatory)

1. **Read `curriculum.json`** for the target topic's `id`, `tag`, `short`, `text`, `requires`, stage position, and linked exercises or GPU labs.
2. **Read the immediately preceding chapter(s)** listed in `requires` (and `reference-cheatsheet.html` if touching Gemma 4, LoRA, serving, or voice specs) so analogies, notation, and numbers stay 100% consistent across the book.
3. **Lock the prerequisite boundary:** Never lean on a concept, term, or equation introduced later in the spine. If a forward pointer helps motivation ("in Stage 4 we'll compress this to 4-bit"), label it clearly as a preview and never depend on it for understanding today's mechanism.

## Phase 2: Blueprint Before HTML

Draft a tight internal blueprint covering these five elements before touching the `.html` file:

1. **Pain + Payoff (Hook):** A concrete hardware wall, OOM crash, latency stall, or naive model failure with real numbers you can trace in your head — paired with the exact capability this unlocks for Capstone 1 (Gemma 4 text) or Capstone 2 (cloned-voice phone agent).
2. **One Running Physical Anchor:** Pick **one** everyday physical or geometric analogy (e.g., 8 Michelin chefs vs. 10,000 prep cooks; sticky-note deltas on a printed encyclopedia; a narrow phone wire slicing off cymbals above 3.4 kHz). Carry it from Section 1 through the summary, and write an explicit **"Where this analogy breaks"** callout/paragraph so the reader never over-extrapolates.
3. **The First-Principles Derivation Ladder:** Structure Sections 2–5 as a question-led discovery chain — never a static list of definitions:
   - **Question → Naive Attempt → Exact Break:** Start with the simplest thing a Python programmer would try, plug in 2–4 numbers, and watch it break concretely.
   - **Hand-Traced Toy Numbers:** Show exact arithmetic on a tiny 2×3 matrix, 4-token sequence, or 4-sample waveform where every multiply, add, and shape is visible.
   - **Visual / Interactive Model:** Let the reader *see* the mechanism move (SVG or `assets/viz.js` interactive widget) before formalizing it.
   - **Plain English → Formal Name & Equation:** Give the jargon *only after* the reader has already invented the idea.
   - **Tiny Pure-Python / NumPy Build (≤15 lines per block):** Prove there is zero magic underneath before introducing the library wrapper (`torch`, `transformers`, `trl`, `peft`, `vLLM`, `Qwen3-TTS`, `Pipecat`).
   - **1-to-1 Bridge + Production Gotchas:** Map each toy line onto the real production stack, expose the real failure modes missing from `gemma.ai` / vendor docs, and state explicitly **when NOT to use this**.
4. **Scope & Pacing Budget:**
   - **Visible core path:** ~2,000–3,500 words (excluding collapsed `details.aside`).
   - **Sections:** 5–8 numbered `h2` sections (`#s1`..`#sN`), each titled as a concrete question or mental-model step.
   - **Visual rhythm:** First visual in `s1` or `s2`; **never more than 2 consecutive numbered sections without a visual** (`.figure` SVG, interactive widget, or `pre.diagram`).
   - **Depth offloading:** Put heavy algebraic proofs, alternative frameworks, or secondary model variants inside collapsed `<details class="aside deeper">`, and put a second intuitive angle for tricky steps inside `<details class="aside another">`.
5. **Quick Checks (5–8 total):** Place one check right after each major mental-model leap.
   - Every check must test **causal prediction, boundary behavior, or a real production bug** ("What happens to X if you double Y while holding Z fixed?").
   - Every distractor option must be a plausible misconception — never a joke or obvious giveaway.
   - `.fb.wrong` must re-explain the core idea from a **second angle**, not repeat `.fb.right` word-for-word.

## Phase 3: Compute Every Number — Zero Eyeballing

Before writing a single calculation into prose, tables, SVGs, or JS widgets:
- Run `python3` to verify every FLOP count, byte count, GB conversion, tensor shape, gradient step, quantization error, sample rate, and latency sum.
- Execute every pure-Python / NumPy code snippet shown in the chapter to confirm it runs cleanly and produces the exact numbers quoted in the text.

## Phase 4: Anti-Slop Prose Rules

- **Voice:** Address the collective reader as "you". Sound like a thoughtful, sharp senior engineer explaining at a whiteboard — clear, direct, curious, never academic or salesy.
- **Zero definition-first openers:** Never begin a chapter or section with "X is a method in machine learning that..."
- **Banned filler words:** Never write *"simply"*, *"obviously"*, *"just"* (when minimizing difficulty), *"trivially"*, *"easily"*, *"it is easy to see"*, *"delve into"*, *"unlock the power of"*, or *"in today's fast-paced AI landscape"*.
- **Zero Markdown leakage in HTML:** Always use `<code>...</code>` (never raw `` `backticks` ``), `<b>`/`<em>` (never `**bold**`), and HTML-escape special tokens (`&lt;|turn&gt;`, `&lt;turn|&gt;`).
- **Zero exercise spoilers:** Link to the local CPU exercise(s) and GPU lab(s) in `#exercises` without revealing exercise implementations or drop-in solutions.

## Phase 5: Canonical Chapter Order & Build Verification

Follow this exact flow (full HTML patterns in `references/html-components.md`):
1. `<header class="chapter-head">` + plain-English 2–3 sentence hook + `.learn-list` + `How to read this` line linking every prerequisite in `requires`.
2. `#s1` Why do we even need this? (`.story` + early visual + Capstone payoff).
3. `#s2`..`#sN-1` Question-led bottom-up rebuild (`Naive → Break → Analogy → Toy Numbers → Visual → Formal Name → Tiny Code`) interleaved with quick checks and collapsed `details.aside`.
4. Final numbered section: Real production gotchas, 1-to-1 stack bridge, and when NOT to use this.
5. `#summary` ("What to remember" — 4–6 crisp engineering laws), `<div class="review" id="review"></div>`, `#exercises` (linked `.exercise` cards for workbench / CPU `pytest` / GPU lab), and `<nav class="chapter-nav">`.

When drafting is complete:
1. Remove `<meta name="status" content="outline">` from `<head>`.
2. Run `python3 tools/check_chapter.py <page.html>` and fix all errors/warnings.
3. Run `python3 tools/build.py` and verify zero prerequisite warnings.
4. Hand off to **`visuals-and-layout`**, then **`review-chapter`** before considering the chapter done.
