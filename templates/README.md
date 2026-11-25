# Templates and house style (`gpu/lab`)

`python3 tools/new.py ...` copies these templates into the right subject and
regenerates `assets/curriculum.js`.

## Book chapters (`concept.html`)
- Same visual, analogy-first book format as `swe-lab`, focused on **applied open-source AI engineering** (architectures, fine-tuning, serving, audio/voice, chaining) rather than interview prep.
- Target **~2,000–3,500 visible words**, **6–8 numbered sections**, **5–8 quick checks**, early visual in Section 1–2, no more than 2 consecutive sections without a visual (`.figure`, SVG, or `pre.diagram`), and secondary deep dives tucked inside `details.aside.deeper`.
- Use `"gpu-lab:"` localStorage prefix and CSS theme tokens (`var(--accent)`, `--ok`, `--warn`, `--bad`, `--accent-2`, `--brand`) so all four themes work cleanly offline.

## CPU Exercises (`exercise.py`, `test_exercise.py`)
- Must run locally with **zero GPU** (`python3 -m pytest`).
- Test exact engineering invariants (VRAM calculations, `-100` completion-only loss masking, LoRA math & merging, voice latency budgets & barge-in reconciliation).
- Stubs always raise `NotImplementedError`. Never commit solutions into stubs.

## Applied ML Worksheets
- `eval-spec.md`: define golden test sets and baselines *before* renting GPUs.
- `experiment-log.md`: log every training run, eval delta, error bucket, and cost.
- `gpu-runbook.md`: reproducible on-demand cloud GPU recipe with teardown checks.
- `capstone-plan.md`: architecture diagram, latency/cost SLAs, and milestones.
