# §07 Chaining Models & Real-Time Phone Calls

> Stage 6 (Capstone 2): rebuilding Deepgram Flux's natural duplex feel with open weights — BF16 Gemma 4 audio-IN vs. Parakeet STT, <800 ms budgets, barge-in reconciliation, Pipecat/LiveKit, and live SIP phone calls.

Open `index.html` in this folder for the interactive dashboard.

## Topics

- [ ] `07.01` **[P0]** **Gemma 4 Audio-IN FT (BF16 LoRA) vs. Streaming STT** — Fine-tuning Gemma 4 E2B/E4B/12B on domain/8 kHz speech in BF16 LoRA (avoiding NF4 degradation) vs. dedicated streaming STT (Parakeet TDT 0.6B, Whisper Turbo, Qwen3-ASR).
- [ ] `07.02` **[P0]** **The <800 ms mouth-to-ear latency budget & speculative prefill** — Budgeting ingress jitter, VAD/endpointing, STT, LLM TTFT, and TTS TTFA — and overlapping speculative LLM prefill on EagerEndOfTurn.
- [ ] `07.03` **[P0]** **Semantic turn detection & barge-in state reconciliation** — Acoustic VAD vs. semantic end-of-turn, canceling in-flight LLM+TTS within 200 ms on caller interruption, and reconciling exact text_spoken vs. text_remaining.
- [ ] `07.04` **[P0]** **Spoken-register Gemma 4 + live phone calls (Pipecat/LiveKit + SIP)** — Fine-tuning Gemma 4 for the ear (short interrupt-safe turns, zero markdown, mid-call tools) and bridging STT + vLLM + cloned TTS onto live SIP/Twilio 8 kHz phone lines.
- [ ] `07.05` **[P1]** **Multi-model chaining & routing patterns** — Chaining fast routers (E2B) → specialist fine-tuned Gemma 4 (12B) → speculative StreamRAG/tools during caller speech → guardrails → cloned streaming TTS.
- [ ] `07.06` **[P2]** **Enterprise telephony hardening (8 kHz, AEC & entity accuracy)** — Surviving G.711 μ-law/Opus compression, jitter buffers, acoustic echo cancellation, background noise, and alphanumeric/phone-number entity stress tests.
