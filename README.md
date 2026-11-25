# gpu/lab

Our collective's **zero-abstraction, first-principles** open-source AI engineering study book and lab — reasoning bottom-up from basic Python, matrices, and GPU hardware physics to toy Transformers, **Gemma 4** fine-tuning and serving, **voice cloning**, **<800 ms live phone agents**, and **native full-duplex speech-to-speech**.

Assumes only basic Python fluency (use [`swe-lab`](https://github.com/Daniishkhan/swe-lab) if you want a Python refresher). Zero prior ML, PyTorch, calculus, or audio background is assumed.

## Two Real Capstones

1. **Capstone 1 (Text):** Fine-tune **Gemma 4** (`E4B`/`12B`) on real-world examples, build automated held-out evals *before* renting GPUs, merge/quantize cleanly (QAT), and serve behind `vLLM` / `SGLang` with MTP speculative decoding and concurrency load tests.
2. **Capstone 2 (Voice & Phone Calls):** Chain streaming STT (`Parakeet TDT` / `Gemma 4` BF16 audio-IN) + spoken-register fine-tuned **Gemma 4** + cloned streaming TTS (`Qwen3-TTS` / `Chatterbox` / `Orpheus`) in **Pipecat / LiveKit** over real SIP/Twilio `8 kHz` phone calls under `<800 ms` mouth-to-ear — then benchmark head-to-head against native full-duplex S2S (`Moshi` / `PersonaPlex 7B` / `NemotronLabs VoiceChat 11B`).

## Quick Start

```bash
open index.html                   # chapter spine dashboard (100% offline, no server needed)
open workbench.html               # offline GPU VRAM & Voice Latency calculators
make setup                        # optional .venv with pytest + numpy (zero GPU needed)
make test                         # run all local CPU exercises (fail until solved)
make one K=gpu_roofline           # run one exercise
make lint                         # lint all completed chapters (offline markup, themes, pacing)
make progress                     # run tests + update pass badges on subject pages
make build                        # validate prerequisite order & regenerate assets/curriculum.js
```

## Working with Gemini & Agent Skills

This repository is built for **Gemini** (Gemini CLI and Google Antigravity) using two native mechanisms:

- **[`GEMINI.md`](GEMINI.md)** — always-on project rules, first-principles standards, and hard invariants loaded automatically into every session.
- **[`.agents/skills/`](.agents/skills/)** — on-demand workflow skills discovered natively by both Gemini CLI and Google Antigravity without cluttering context:

| Skill | Purpose |
|---|---|
| [`write-chapter`](.agents/skills/write-chapter/SKILL.md) | Write or rewrite a visual HTML chapter from first principles (with [`html-components.md`](.agents/skills/write-chapter/references/html-components.md)) |
| [`visuals-and-layout`](.agents/skills/visuals-and-layout/SKILL.md) | Build intuition-first SVGs & `assets/viz.js` widgets and verify 4-theme contrast + mobile layout |
| [`review-chapter`](.agents/skills/review-chapter/SKILL.md) | Adversarial 4-lens review (first-principles clarity, Python-verified math, production gotchas, QA) |
| [`author-exercise`](.agents/skills/author-exercise/SKILL.md) | Author a zero-GPU pure-Python/NumPy exercise + adversarial `pytest` suite (verified out-of-repo) |
| [`write-lab`](.agents/skills/write-lab/SKILL.md) | Write a reproducible cloud GPU lab runbook (`labs/*.md`) with VRAM/cost sizing and teardown checks |
| [`teach`](.agents/skills/teach/SKILL.md) | Interactive Socratic first-principles tutoring and stage milestone quizzes |
| [`coach`](.agents/skills/coach/SKILL.md) | Zero-spoiler progressive hint ladder and staff-engineer review for CPU exercises and GPU labs |

### Recommended Authoring Pipeline

1. **Book chapter:** Activate `write-chapter` → `visuals-and-layout` → `review-chapter`, then verify with `python3 tools/check_chapter.py <page.html>`, `python3 tools/build.py`, and (when Playwright is installed) `node tools/check_page.js <page.html>`.
2. **CPU exercise:** Activate `author-exercise`, verify with `python3 tools/check_exercise.py <mod> --pass /tmp/ref.py --fail /tmp/bad.py`, delete the temp files outside the repo, and run `python3 tools/build.py`.
3. **Cloud GPU lab:** Activate `write-lab` and keep `labs/README.md` + `curriculum.json` in sync.

## The Zero-Abstraction Spine

| Stage | Focus | Toy Build / Milestone |
|---|---|---|
| **Phase 0A** | **Python primer & math fluency** (slicing, dicts, `zip`, comprehensions, math formulas, 2D grids, basic classes & `yield` batches) | `python_warmup.py`, `python_math_drills.py`, `python_classes_and_batches.py` |
| **Phase 0B** | **Vectors, matrices, everyday NumPy & GPUs** (norms, dot products, `@` shapes, slicing/`axis`/broadcasting/masks → **What is a GPU?**) | `vector_math.py`, `matmul_shapes.py`, `numpy_habits.py`, `gpu_roofline.py` |
| **Stage 1** | What does "learning" mean? Loss, gradient descent, **40-line autograd**, toy MLP → **PyTorch & HF** | `micro_autograd.py` + tiny next-char LM |
| **Stage 2** | **Inventing the Transformer** (BPE, Q/K/V attention, RoPE, 120-line toy GPT) → **Gemma 4's 4 architectures** | 120-line toy GPT + `labs/01-gemma4-first-inference.md` |
| **Stage 3** | **Fine-tuning Gemma 4** (exact VRAM math, LoRA from scratch, eval-first data, `-100` masking, SFT + DPO/GRPO) | `vram_budget.py`, `lora_math.py`, `loss_masking.py` + `labs/02-gemma4-qlora-sft.md` |
| **Stage 4** | **Inference physics & serving** (4-bit quantization & KV cache from scratch, QAT, `vLLM`/`SGLang`, MTP) | **Capstone 1 Shipped** (production Gemma 4 text API) |
| **Stage 5** | **What is sound?** Waveforms, 8 kHz phone physics, spectrograms, **RVQ audio codecs**, voice cloning & streaming TTS | `labs/03-qwen3-tts-voice-clone.md` (<150 ms TTFA cloned voice) |
| **Stage 6** | **Chaining & live phone calls** (Gemma audio-IN vs. Parakeet STT, `<800 ms` budget, semantic turn & barge-in, Pipecat/LiveKit + SIP) | `voice_pipeline_budget.py` + **Capstone 2 Shipped** (`labs/04-voice-agent-phone-loop.md`) |
| **Stage 7** | **Frontier Full-Duplex S2S & Production** (`Moshi`/`PersonaPlex`/`VoiceChat` vs. cascade, audio traces, FSDP2, GPU unit economics) | Production runbook & cascade vs. full-duplex decision memo |

Plus a **Parallel Capstone Journal** (~1h/week) and 3 pickable **Specialist Packs** (`Gemma Specialists`, `Enterprise Telephony`, `Deep Training & Distillation`).

## Scaffolding New Material

```bash
python3 tools/new.py concept  00.01 python-refresher  "Python refresher & everyday idioms"
python3 tools/new.py exercise 03.02 attention_scratch "Causal self-attention from scratch"
python3 tools/new.py eval     "Capstone 1 structured extraction"
python3 tools/new.py exp      "Gemma 4 E4B LoRA run 01"
python3 tools/new.py runbook  "PersonaPlex stereo LoRA"
python3 tools/new.py capstone "Cloned-voice phone agent"
```

## Keyboard Shortcuts (All Pages)

<kbd>[</kbd> toggle sidebar · <kbd>]</kbd> toggle contents rail · <kbd>t</kbd> next theme (Ayu Dark → Mirage → Gruvbox → Light) · <kbd>a</kbd> appearance · <kbd>/</kbd> jump to · <kbd>e</kbd>/<kbd>c</kbd> expand/collapse asides
