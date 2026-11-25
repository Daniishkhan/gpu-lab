# Cloud GPU Lab Runbooks (`labs/`)

Every lab here is designed for **on-demand cloud GPUs** (RunPod, Modal, Lambda,
or Google Colab Pro). Complete the matching local CPU exercises first so you
never debug trivial bugs while paying per minute for a GPU.

## Quick GPU Cheat Sheet

| GPU | VRAM | Typical Rate | Best Used For |
|---|---|---|---|
| **NVIDIA L4** | 24 GB | ~$0.70/hr | Gemma 4 E2B/E4B/12B QLoRA, E2B/E4B BF16 Audio LoRA, Qwen3-TTS / Chatterbox cloning & LoRA, vLLM serving (E4B/12B Q4) |
| **NVIDIA L40S** | 48 GB | ~$1.15/hr | Gemma 4 12B BF16 LoRA & BF16 serving, co-locating STT + vLLM Gemma 4 + TTS on one card |
| **NVIDIA A100 / H100** | 80 GB | ~$1.85–$2.90/hr | Gemma 4 26B-A4B MoE Split-LoRA, Full FT, Moshi / PersonaPlex 7B LoRA, NemotronLabs VoiceChat 11B |

## Runbooks in Order

1. [`01-gemma4-first-inference.md`](01-gemma4-first-inference.md) — Stage 2 (`03.04`): Run `gemma-4-E4B-it` on 1× L4 and profile TTFT, decode tok/s, and peak VRAM.
2. [`02-gemma4-qlora-sft.md`](02-gemma4-qlora-sft.md) — Stage 3 (`04.05`): Eval-first Gemma 4 SFT with TRL + PEFT (and Unsloth), `-100` loss masking, merging, and vLLM parity check.
3. [`03-qwen3-tts-voice-clone.md`](03-qwen3-tts-voice-clone.md) — Stage 5 (`06.04`–`06.05`): Zero-shot 3 s cloning and speaker LoRA on Apache 2.0 `Qwen3-TTS` & MIT `Chatterbox-Turbo` + 8 kHz phone simulation.
4. [`04-voice-agent-phone-loop.md`](04-voice-agent-phone-loop.md) — Stage 6 (`07.04`): Wire streaming STT + vLLM fine-tuned Gemma 4 + cloned streaming TTS in Pipecat/LiveKit onto a live SIP/Twilio phone call.

> **Golden habit:** Always push adapters, merged checkpoints, and eval JSON to
> Hugging Face Hub or cloud storage **before** terminating your GPU pod, and
> shut the pod down the minute a run finishes.
