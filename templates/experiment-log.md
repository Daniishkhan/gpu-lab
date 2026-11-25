# Experiment Log: {{TITLE}}

- **Date:** {{DATE}}
- **Capstone / Goal:** (Capstone 1 Text / Capstone 2 Voice / Full-Duplex)
- **Hypothesis:** What single change are we testing, and what metric must move?

## Setup
- **Base checkpoint:** (e.g., `google/gemma-4-E4B-it`)
- **Dataset version & size:** (train / val / test counts)
- **Method & key hyperparams:** (QLoRA vs BF16 LoRA, `r`, `alpha`, `lr`, epochs, batch size, masking verified?)
- **GPU & runtime:** (e.g., `1× L4 24GB`, `24 min`, `~$0.28`)

## Results vs. Baseline

| Metric | Baseline (Zero-shot / Prior Run) | This Run | Delta |
|---|---|---|---|
| Held-out task score | | | |
| General regression slice | | | |
| Val loss / token acc | | | |
| p95 Latency (TTFT or TTFA) | | | |

## Error Forensics (inspect 10 failures by eye)
1. Failure pattern A:
2. Failure pattern B:

## Decision
- [ ] Keep checkpoint · [ ] Fix data · [ ] Adjust hyperparams · [ ] Discard
- **Next single change:**
