# Lab 03 · Voice Cloning & Custom Speaker LoRA (Qwen3-TTS & Chatterbox)

- **Topic:** `06.04`, `06.05` (Stage 5 · Capstone 2 Voice)
- **Recommended GPU:** `1× NVIDIA L4 (24 GB)`
- **Estimated VRAM / Runtime / Cost:** `~8–16 GB` · `~30–60 min` · `~$0.50–$0.80`

## Pre-Flight Checks (do locally first)
- [ ] Prepare **consented** target speaker audio:
  - **Zero-shot cloning:** 1 clean 5–10 second WAV (24 kHz mono, no music/reverb) + exact transcript.
  - **Speaker LoRA fine-tuning:** 5–20 minutes of clean speech split into 5–15 second clips with verified transcripts (Stage 5 audio hygiene pipeline).
- [ ] Prepare a 20-sentence telephony test script containing phone numbers, dollar amounts, dates, acronyms, and conversational interjections.

## 1. Zero-Shot Cloning Benchmark (Two Apache/MIT Leaders)

Compare both open models on the exact same reference clip and 20-sentence test script:

| Model | License | Strengths | Target Latency |
|---|---|---|---|
| **Qwen3-TTS** (`0.6B-Base` / `1.7B-Base`) | Apache 2.0 | 3-second zero-shot cloning, 12 Hz multi-codebook tokenizer, dual-track streaming, clean LoRA speaker tuning | ~97 ms TTFA |
| **Chatterbox / Chatterbox-Turbo** | MIT | Ultra-low streaming latency, expressive paralinguistic tags (`<laugh>`, `<sigh>`), 23 languages | ~75 ms TTFA |

## 2. The 8 kHz Phone-Line Reality Test (Do NOT Skip!)

Studio 24 kHz audio sounds gorgeous on headphones and can still sound robotic or muffled over a real phone call. Round-trip every candidate voice through G.711 μ-law telephony compression with `ffmpeg`:

```bash
ffmpeg -y -i studio_24k.wav -ar 8000 -ac 1 -c:a pcm_mulaw phone_8k.wav
ffmpeg -y -i phone_8k.wav -ar 16000 -ac 1 phone_roundtrip_16k.wav
```

Listen to `phone_roundtrip_16k.wav` and run it through an open STT model (`Parakeet TDT` or `Whisper`) to compute **round-trip WER** — especially on phone numbers, confirmation codes, and names!

## 3. Speaker-Specific LoRA Fine-Tuning (`Qwen3-TTS-12Hz-1.7B-Base`)
When zero-shot cloning drifts in accent, cadence, or timbre across multi-turn phone calls:
1. Extract 12 Hz discrete audio codec tokens for all cleaned 5–15 s speaker clips.
2. Fine-tune a lightweight LoRA adapter on `Qwen3-TTS-12Hz-1.7B-Base` (24 GB VRAM fits cleanly on 1× L4).
3. Sweep LoRA merge scale (commonly `0.30–0.65`) and evaluate **speaker cosine similarity** vs. **round-trip WER** vs. **naturalness** — too high a scale overfits and sounds stiff; too low loses the speaker's cadence.
4. Log your zero-shot vs. LoRA numbers in `workbench.html` and save checkpoints before terminating the pod.
