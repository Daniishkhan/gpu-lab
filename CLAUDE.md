# gpu-lab: how to work in this repo

A **no-abstraction**, bottom-up open-source AI engineering study book and lab —
starting from basic Python fluency (reusing `swe-lab` for core Python) and
reasoning all the way up from matrices, GPU hardware, a 40-line autograd engine,
and a 120-line toy Transformer to **Gemma 4** fine-tuning, serving, voice
cloning, model chaining, live phone calls, and native full-duplex speech models.

This is NOT an interview prep repo. The goal is deep architectural mastery and
shipping real, fast, cost-aware open-weight systems.

## How we teach (zero-abstraction first principles)

Assume **zero prior ML, PyTorch, calculus, or audio knowledge** — only basic
Python fluency. Never hand-wave a library call (`SFTTrainer`, `vLLM`, `Mimi`,
`Pipecat`) until Danish has seen or built the tiny toy version underneath it:

1. **Start from "why should I care?" (pain + payoff):** open with a concrete
   hardware limit, OOM crash, phone-call latency stall, or toy failure with
   small numbers you can trace in your head.
2. **One running physical analogy:** carry one concrete physical anchor across
   the whole rebuild (e.g., 8 PhD chefs vs. 10,000 line cooks for CPU vs. GPU;
   sticky-note deltas on a printed encyclopedia for LoRA; a narrow phone wire
   chopping off cymbals for 8 kHz μ-law), stating explicitly where it breaks.
3. **Rebuild bottom-up (`Question → Toy naive attempt → Break → Fix`):**
   tiny 2–4 number examples first → visual diagram → plain English → formal
   name → small pure-Python/NumPy build → real framework (`PyTorch` / `TRL` /
   `vLLM` / `Pipecat`).
4. **Protect the first-pass core path:** ~2,000–3,500 visible words per full
   chapter, early visual in Section 1–2, max 2 consecutive sections without a
   visual, secondary deep dives tucked into collapsed `details.aside.deeper`.
5. **Check intuition, not trivia:** ask predictions ("what happens to decode
   tok/s if we double GPU FLOPs without doubling VRAM bandwidth?"), never
   memorized formulas.

## Hard rules

1. **Never write exercise solutions** in the repo or in chat. Stubs in
   `sections/*/exercises/*.py` raise `NotImplementedError`. Verify test suites
   using temporary reference files in a scratch directory *outside* the repo
   via `tools/check_exercise.py`, then delete the scratch files.
2. **Keep localStorage isolated:** every page uses the `"gpu-lab:"` prefix
   (never `"swe-prep:"` or `"model-lab:"`).
3. **No external dependencies in HTML pages:** no CDNs, frameworks, or `fetch()`;
   everything works offline from `file://` using `assets/viz.js` and CSS theme
   tokens (`var(--accent)`, `--ok`, `--warn`, `--bad`, `--accent-2`, `--brand`).
4. **Local CPU exercises run with zero GPU:** pure Python / NumPy exercises
   verify every core invariant locally (`pytest`); cloud GPU runs live in
   `labs/*.md` with explicit GPU sizing and cost estimates.
5. **Exercise module names are unique repo-wide** (no `__init__.py` files).
6. After adding or renaming a page or exercise, run `python3 tools/build.py`
   and commit the regenerated `assets/curriculum.js`.
7. **Keep the prerequisite order strictly monotonic:** every topic's `requires`
   in `curriculum.json` must appear earlier on the spine; `tools/build.py`
   enforces this automatically.

## Skills (`.claude/skills/`)

| When | Skill |
|---|---|
| Danish wants to understand a concept from zero abstractions, or be quizzed | `teach` |
| Danish is stuck on a local exercise or GPU lab bug | `coach` |
| Writing or rewriting a visual book chapter | `write-chapter` → `visuals-and-layout` → `review-chapter` |

## Commands

```bash
python3 -m pytest -k <name>                       # run one local CPU exercise
python3 tools/build.py                            # regenerate assets/curriculum.js
python3 tools/new.py concept 01.01 slug "Title"   # also: exercise, eval, exp, runbook, capstone
python3 tools/check_exercise.py <name> --pass ref.py --fail bad.py
node tools/check_page.js <page.html> [--shots DIR]
```
