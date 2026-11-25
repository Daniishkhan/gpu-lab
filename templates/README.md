# Templates & House Style (`gpu/lab`)

`python3 tools/new.py ...` copies these templates into the right section and regenerates `assets/curriculum.js`. Full authoring standards live in [`GEMINI.md`](../GEMINI.md) and [`.agents/skills/`](../.agents/skills/).

## Book Chapters (`concept.html`)
- First-principles, visual, analogy-first chapters built via the **`write-chapter` → `visuals-and-layout` → `review-chapter`** skill pipeline.
- Target **~2,000–3,500 visible words**, **5–8 numbered sections**, **5–8 causal prediction quick checks**, an early visual in Section 1–2, at most 2 consecutive sections without a visual (`.figure`, `<svg>`, or `pre.diagram`), and secondary deep dives tucked inside `details.aside.deeper`.
- Zero external dependencies (`file://` offline safe), `"gpu-lab:"` localStorage prefix, and CSS theme tokens only (`var(--accent)`, `--ok`, `--warn`, `--bad`, `--accent-2`, `--brand`).
- Verify every completed chapter with `python3 tools/check_chapter.py <page.html>` and `python3 tools/build.py`.

## CPU Exercises (`exercise.py`, `test_exercise.py`)
- Authored with the **`author-exercise`** skill. Must run locally with **zero GPU** (`python3 -m pytest`).
- Prove one concrete engineering invariant locally (roofline math, micro-autograd, VRAM accounting, LoRA merging, `-100` loss masking, `<800 ms` latency budgets & barge-in reconciliation).
- Stubs always raise `NotImplementedError`. Verify test suites via `tools/check_exercise.py` using temporary scratch files *outside* the repo, then delete those scratch files.

## Applied ML Worksheets & Runbooks
- `eval-spec.md`: define golden held-out test sets and baselines *before* renting GPUs.
- `experiment-log.md`: log every training run, eval delta, error bucket, and cost.
- `gpu-runbook.md`: reproducible on-demand cloud GPU recipe with pinned versions and teardown checks (see `write-lab` skill).
- `capstone-plan.md`: end-to-end architecture diagram, latency/cost SLAs, and milestones.
