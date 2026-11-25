# gpu/lab

A **no-abstraction** open-source AI engineering study book and lab — reasoning
bottom-up from basic Python, matrices, and GPU hardware to toy Transformers,
**Gemma 4** fine-tuning & production serving, **voice cloning**, **chaining
models for live phone calls**, and **native full-duplex speech-to-speech**.

Assumes only basic Python fluency (use [`swe-lab`](https://github.com/Daniishkhan/swe-lab)
for core Python foundations). Zero prior ML, PyTorch, calculus, or audio
background assumed.

## Two Real Capstones

1. **Capstone 1 (Text):** Fine-tune **Gemma 4** (`E4B`/`12B`) on your own
   real-world examples, build automated evals *before* training, merge/quantize
   cleanly (QAT), and serve behind `vLLM` / `SGLang` with MTP speculative
   decoding and concurrency load tests.
2. **Capstone 2 (Voice & Phone Calls):** Chain streaming STT (`Parakeet TDT` /
   `Gemma 4` BF16 audio-IN) + spoken-register fine-tuned **Gemma 4** + cloned
   streaming TTS (`Qwen3-TTS` / `Chatterbox` / `Orpheus`) in **Pipecat /
   LiveKit** over real SIP/Twilio `8 kHz` phone calls under `<800 ms`
   mouth-to-ear — then benchmark head-to-head against native full-duplex S2S
   (`Moshi` / `PersonaPlex 7B` / `NemotronLabs VoiceChat 11B`).

## Quick start

```bash
open index.html                   # chapter spine dashboard (offline, no server needed)
open workbench.html               # offline GPU VRAM & Voice Latency calculators
make setup                        # optional .venv with pytest + numpy (zero GPU needed)
make test                         # run all local CPU exercises (fail until you solve them)
make one K=matmul_shapes          # run one exercise
make progress                     # run tests + update pass badges on subject pages
make build                        # regenerate assets/curriculum.js after edits
```

## The Zero-Abstraction Spine

| Stage | Focus | Toy Build / Milestone |
|---|---|---|
| **Phase 0** | Python → vectors, `@` matrix shapes, **What is a GPU?** (FLOPs vs. memory bandwidth) | `matmul_shapes.py` + `gpu_roofline.py` |
| **Stage 1** | What does "learning" mean? Loss, gradient descent, **40-line autograd**, toy MLP → **PyTorch & HF** | `micro_autograd.py` + tiny next-char LM |
| **Stage 2** | **Inventing the Transformer** (BPE, Q/K/V attention, RoPE, 120-line toy GPT) → **Gemma 4's 4 architectures** | 120-line toy GPT + `labs/01-gemma4-first-inference.md` |
| **Stage 3** | **Fine-tuning Gemma 4** (exact VRAM math, LoRA from scratch, eval-first data, `-100` masking, SFT + DPO/GRPO) | `vram_budget.py`, `lora_math.py`, `loss_masking.py` + `labs/02-gemma4-qlora-sft.md` |
| **Stage 4** | **Inference physics & serving** (4-bit quantization & KV cache from scratch, QAT, `vLLM`/`SGLang`, MTP) | **Capstone 1 Shipped** (production Gemma 4 text API) |
| **Stage 5** | **What is sound?** Waveforms, 8 kHz phone physics, spectrograms, **RVQ audio codecs**, voice cloning & streaming TTS | `labs/03-qwen3-tts-voice-clone.md` (<150 ms TTFA cloned voice) |
| **Stage 6** | **Chaining & live phone calls** (Gemma audio-IN vs. Parakeet STT, `<800 ms` budget, semantic turn & barge-in, Pipecat/LiveKit + SIP) | `voice_pipeline_budget.py` + **Capstone 2 Shipped** (`labs/04-voice-agent-phone-loop.md`) |
| **Stage 7** | **Frontier Full-Duplex S2S & Production** (`Moshi`/`PersonaPlex`/`VoiceChat` vs. cascade, audio traces, FSDP2, GPU unit economics) | Production runbook & cascade vs. full-duplex decision memo |

Plus a **Parallel Capstone Journal** (~1h/week) and 3 pickable **Specialist Packs** (`Gemma Specialists`, `Enterprise Telephony`, `Deep Training & Distillation`).

## Adding material

```bash
python3 tools/new.py concept  01.01 vectors-and-dots  "From Python loops to vectors"
python3 tools/new.py exercise 03.02 attention_scratch "Causal self-attention from scratch"
python3 tools/new.py eval     "Capstone 1 structured extraction"
python3 tools/new.py exp      "Gemma 4 E4B LoRA run 01"
python3 tools/new.py runbook  "PersonaPlex stereo LoRA"
python3 tools/new.py capstone "Cloned-voice phone agent"
```

## Keyboard shortcuts (all pages)

<kbd>[</kbd> toggle sidebar · <kbd>]</kbd> toggle contents rail · <kbd>t</kbd> next theme (Ayu Dark → Mirage → Gruvbox → Light) · <kbd>a</kbd> appearance · <kbd>/</kbd> jump to · <kbd>e</kbd>/<kbd>c</kbd> expand/collapse asides
