# Eval Specification: {{TITLE}}

- **Date:** {{DATE}}
- **Task in one sentence:**
- **Why fine-tuning (instead of only prompting or RAG)?**

## Golden Evaluation Set
- **Test set size (held out, NEVER in training):** (target 100–300 real examples)
- **Hard edge cases explicitly included:**
- **General-capability regression slice (catch catastrophic forgetting):** (20–50 unrelated prompts)

## Grading Metrics
1. **Deterministic / verifiable metric:** (JSON schema valid %, exact field match %, WER %, tool-arg match %)
2. **Quality / human / LLM-as-judge rubric:** (1–5 scale with concrete failure examples)
3. **Production SLA:** (max p95 TTFT / TTFA, max cost per 1M tokens or per call minute)

## Baselines (measure BEFORE touching a training GPU)
- Zero-shot base (`-it`):
- Few-shot prompt (5 examples):
- Teacher model (e.g. Gemma 4 31B):
- **Ship threshold to beat:**
