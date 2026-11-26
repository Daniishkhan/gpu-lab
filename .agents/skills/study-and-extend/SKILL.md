---
name: study-and-extend
description: Interactive chapter tutoring and safe live in-place chapter extensions inside Antigravity IDE's Study Cockpit (make study + Simple Browser live reload), respecting offline HTML rules, theme tokens, and curriculum prerequisites.
---

# Study & Live-Extend a Chapter (`gpu/lab`)

Use this skill when the learner is reading a chapter inside **Antigravity IDE's Simple Browser** (`make study` at `http://127.0.0.1:8000`) and asks to explain a tricky concept, trace a small example, or **extend a chapter in place** with a clearer walkthrough, diagram, or aside.

## Mode A: Interactive Explanation / Walkthrough (No File Edits)

1. **Ground in the chapter:** Read the target chapter in `book/sections/<NN>-<slug>/concepts/*.html` and check its `requires` in `curriculum.json`.
2. **Reuse the chapter's running analogy:** Explain using the same physical anchor the chapter already built (never invent three conflicting metaphors), and state clearly where the analogy breaks.
3. **Hand-trace tiny numbers:** Show 2–4 concrete values step by step (verify any arithmetic with `python3` — never eyeball).
4. **Check understanding actively:** End with **one** causal prediction question ("What changes if we double X while keeping Y fixed?") before moving on. Never reveal exercise solutions.

## Mode B: Live In-Place Chapter Extension

When the learner asks to **add** an example, loop trace, diagram, or clarification directly to a chapter so it stays in their personal/collective book:

1. **Protect the core path:**
   - Keep the main visible path crisp (~2,000–3,500 words).
   - Prefer `<details class="aside another">` ("Explain it another way") for alternative intuitive traces, or `<details class="aside deeper">` ("Go deeper") for secondary proofs/edge cases.
   - Only edit core prose directly when fixing genuine ambiguity or filling a real first-principles gap.
2. **Follow all `gpu/lab` HTML invariants:**
   - **100% offline (`file://` & GitHub Pages safe):** zero external URLs, zero `fetch()`.
   - **Zero hardcoded colors:** use only CSS tokens from `book/assets/style.css` (`var(--accent)`, `--accent-2`, `--ok`, `--warn`, `--bad`, `--surface`, `--surface-2`, `--border`, `--text`, `--text-strong`, `--muted`, `--on-accent`, `--*-soft`) so all 4 themes stay readable.
   - **Clean HTML:** use `<code>`, `<b>`, `<em>` (never raw Markdown `` `backticks` `` or `**bold**`), wrap every `<table>` in `<div class="table-wrap">`, give every `.figure` a `.cap`, and escape `<|turn>` / `<turn|>` as `&lt;|turn&gt;`.
   - **Zero exercise spoilers:** never leak exercise implementations into chapter examples.
3. **Verify immediately (triggers live reload in Simple Browser!):**
   ```bash
   python3 tools/check_chapter.py book/sections/<NN>-<slug>/concepts/<chapter>.html
   ```
   Because `make study` watches `book/`, saving the verified chapter automatically reloads the learner's Simple Browser pane at their exact scroll position.
4. **Branch reminder:** If the learner is currently on `study/my-work`, chapter improvements live cleanly under `book/` and can later be cherry-picked to `main` without pulling in solved files from `exercises/` (`make check-main` enforces this).
