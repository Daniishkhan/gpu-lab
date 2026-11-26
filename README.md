# gpu/lab

Our collective's **zero-abstraction, first-principles** open-source AI engineering study book and lab — reasoning bottom-up from basic Python, matrices, and GPU hardware physics to toy Transformers, **Gemma 4** fine-tuning and serving, **voice cloning**, **<800 ms live phone agents**, and **native full-duplex speech-to-speech**.

Assumes only basic Python fluency. Zero prior ML, PyTorch, calculus, or audio background is assumed.

Optimized for **Antigravity IDE** (in-IDE Study Cockpit with live reload, styled Markdown runbooks, auto-`pytest` on save, and loop-by-loop `F5` inline-value debugging) **and 100% offline HTML / GitHub Pages viewing** (`book/`). Phase 0–Stage 1 run completely locally on CPU; cloud GPU labs (`gpu-labs/`) target RunPod pods and SSH GPU VMs once you reach Stage 2+.

## Repository Layout

| Directory | Role |
|---|---|
| [`book/`](book/index.html) | 100% offline visual HTML book (published to GitHub Pages): spine dashboard, chapters, cheatsheets, and GPU/Voice workbench |
| [`exercises/`](exercises/) | Zero-GPU pure-Python & NumPy CPU exercises + adversarial `pytest` suites |
| [`gpu-labs/`](gpu-labs/README.md) | Reproducible cloud GPU runbooks (RunPod / SSH VMs) with VRAM/cost budgets & teardown checks |
| [`journal/`](journal/) | Held-out `evals/`, `experiments/` logs, and `capstones/` plans |
| `scratch/` | Gitignored local sandbox for quick `F5` loop-tracing scripts |
| [`tools/`](tools/) & [`.vscode/`](.vscode/) | Local Study Cockpit (`study.py`), curriculum builder, linters, stub guardrail, and IDE debugger configs |

## Quick Start (Antigravity IDE Study Cockpit)

```bash
make setup                        # create .venv with pytest + numpy (zero GPU needed)
make study                        # launch Study Cockpit at http://127.0.0.1:8000
                                  # in Antigravity IDE: Cmd+Shift+P -> Simple Browser: Show -> http://127.0.0.1:8000
```

Keep `main` clean (unsolved stubs only, enforced by `make check-main`) and do your personal exercise work on a study branch (`git checkout -b study/my-work`).

### Other Handy Commands

```bash
make open                         # open book/index.html directly over file:// (100% offline)
make test                         # run all local CPU exercises (fail until solved)
make one K=gpu_roofline           # run one exercise
make lint                         # lint all completed chapters (offline markup, themes, pacing)
make check-main                   # verify all exercise stubs raise NotImplementedError
make progress                     # run tests + update pass badges on subject pages
make build                        # validate prerequisite order & regenerate book/assets/curriculum.js
```

## Working with Gemini & Antigravity Agent Skills

This repository is built for **Google Antigravity** and **Gemini CLI** using two native mechanisms:

- **[`GEMINI.md`](GEMINI.md)** — always-on project rules, IDE workflow context, first-principles standards, and hard invariants loaded automatically into every session.
- **[`.agents/skills/`](.agents/skills/)** — on-demand workflow skills discovered natively without cluttering context:

| Skill | Purpose |
|---|---|
| [`trace-and-debug`](.agents/skills/trace-and-debug/SKILL.md) | Loop-by-loop Socratic debugging in Antigravity IDE (`pytest` first, tiny iteration tables, `F5` breakpoints, zero spoilers) |
| [`study-and-extend`](.agents/skills/study-and-extend/SKILL.md) | Interactive chapter Q&A and safe live in-place chapter edits (reloads live in Simple Browser via `make study`) |
| [`run-gpu-lab`](.agents/skills/run-gpu-lab/SKILL.md) | Cost-safe RunPod & SSH VM workflow (CPU pre-flight gate, `rsync`/`tmux`, artifact capture, mandatory teardown) |
| [`write-chapter`](.agents/skills/write-chapter/SKILL.md) | Write or rewrite a visual HTML chapter from first principles |
| [`visuals-and-layout`](.agents/skills/visuals-and-layout/SKILL.md) | Build intuition-first SVGs & `book/assets/viz.js` widgets and verify 4-theme contrast + mobile layout |
| [`review-chapter`](.agents/skills/review-chapter/SKILL.md) | Adversarial 4-lens review (first-principles clarity, Python-verified math, production gotchas, QA) |
| [`author-exercise`](.agents/skills/author-exercise/SKILL.md) | Author a zero-GPU pure-Python/NumPy exercise + adversarial `pytest` suite (verified out-of-repo) |
| [`write-lab`](.agents/skills/write-lab/SKILL.md) | Write a reproducible cloud GPU lab runbook (`gpu-labs/<NN>-<slug>/README.md`) |

## Two Real Capstones

1. **Capstone 1 (Text):** Fine-tune **Gemma 4** (`E4B`/`12B`) on real-world examples, build automated held-out evals *before* renting GPUs, merge/quantize cleanly (QAT), and serve behind `vLLM` / `SGLang` with MTP speculative decoding and concurrency load tests.
2. **Capstone 2 (Voice & Phone Calls):** Chain streaming STT (`Parakeet TDT` / `Gemma 4` BF16 audio-IN) + spoken-register fine-tuned **Gemma 4** + cloned streaming TTS (`Qwen3-TTS` / `Chatterbox` / `Orpheus`) in **Pipecat / LiveKit** over real SIP/Twilio `8 kHz` phone calls under `<800 ms` mouth-to-ear — then benchmark head-to-head against native full-duplex S2S (`Moshi` / `PersonaPlex 7B` / `NemotronLabs VoiceChat 11B`).

## The Zero-Abstraction Spine

| Stage | Focus | Toy Build / Milestone |
|---|---|---|
| **Phase 0A** | **Python primer & math fluency** (control flow, data structures, memory model, comprehensions/generators, classes/decorators, stdlib, math formulas & batched generators) | `py_foundations.py`, `py_idioms.py`, `py_internals.py`, `py_toolkit.py`, `python_math_drills.py`, `python_classes_and_batches.py` |
| **Phase 0B** | **Vectors, matrices, everyday NumPy & GPUs** (norms, dot products, `@` shapes, slicing/`axis`/broadcasting/masks → **What is a GPU?**) | `vector_math.py`, `matmul_shapes.py`, `numpy_habits.py`, `gpu_roofline.py` |
| **Stage 1** | What does "learning" mean? Loss, gradient descent, **40-line autograd**, toy MLP → **PyTorch & HF** | `micro_autograd.py` + tiny next-char LM |
| **Stage 2** | **Inventing the Transformer** (BPE, Q/K/V attention, RoPE, 120-line toy GPT) → **Gemma 4's 4 architectures** | 120-line toy GPT + `gpu-labs/01-gemma4-first-inference/` |
| **Stage 3** | **Fine-tuning Gemma 4** (exact VRAM math, LoRA from scratch, eval-first data, `-100` masking, SFT + DPO/GRPO) | `vram_budget.py`, `lora_math.py`, `loss_masking.py` + `gpu-labs/02-gemma4-qlora-sft/` |
| **Stage 4** | **Inference physics & serving** (4-bit quantization & KV cache from scratch, QAT, `vLLM`/`SGLang`, MTP) | **Capstone 1 Shipped** (production Gemma 4 text API) |
| **Stage 5** | **What is sound?** Waveforms, 8 kHz phone physics, spectrograms, **RVQ audio codecs**, voice cloning & streaming TTS | `gpu-labs/03-qwen3-tts-voice-clone/` (<150 ms TTFA cloned voice) |
| **Stage 6** | **Chaining & live phone calls** (Gemma audio-IN vs. Parakeet STT, `<800 ms` budget, semantic turn & barge-in, Pipecat/LiveKit + SIP) | `voice_pipeline_budget.py` + **Capstone 2 Shipped** (`gpu-labs/04-voice-agent-phone-loop/`) |
| **Stage 7** | **Frontier Full-Duplex S2S & Production** (`Moshi`/`PersonaPlex`/`VoiceChat` vs. cascade, audio traces, FSDP2, GPU unit economics) | Production runbook & cascade vs. full-duplex decision memo |

Plus a **Parallel Capstone Journal** (~1h/week) and 3 pickable **Specialist Packs** (`Gemma Specialists`, `Enterprise Telephony`, `Deep Training & Distillation`).

## Scaffolding New Material

```bash
python3 tools/new.py concept  01.01 vectors-and-dots  "Vectors, distance & dot products"
python3 tools/new.py exercise 03.02 attention_scratch "Causal self-attention from scratch"
python3 tools/new.py eval     "Capstone 1 structured extraction"
python3 tools/new.py exp      "Gemma 4 E4B LoRA run 01"
python3 tools/new.py runbook  "PersonaPlex stereo LoRA"
python3 tools/new.py capstone "Cloned-voice phone agent"
```

## Keyboard Shortcuts (All Pages)

<kbd>[</kbd> toggle sidebar · <kbd>]</kbd> toggle contents rail · <kbd>t</kbd> next theme (Ayu Dark → Mirage → Gruvbox → Light) · <kbd>a</kbd> appearance · <kbd>/</kbd> jump to · <kbd>e</kbd>/<kbd>c</kbd> expand/collapse asides
