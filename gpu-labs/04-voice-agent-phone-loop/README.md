# Lab 04 · Live Self-Hosted Cloned-Voice Phone Agent (Capstone 2)

- **Topic:** `07.04` (Stage 6 · Capstone 2 Ship)
- **Recommended GPU:** `1× L40S (48 GB)` (single box co-location) or `2× L4 (24 GB)`
- **Estimated Runtime / Cost:** `~1–2 hr` live call testing · `~$1.50–$2.50`

## Pre-Flight Checks (do locally first)
- [ ] Pass `python3 -m pytest -k voice_pipeline_budget`
- [ ] Verified Capstone 2 spoken-register fine-tuned Gemma 4 (`E4B-it` or `12B-it`) merged & served on `vLLM` (with thinking disabled for fast TTFT!)
- [ ] Verified Lab 03 cloned voice streaming TTS WebSocket (`<150 ms` TTFA)
- [ ] Twilio or SIP trunk test phone number ready

## 1. End-to-End Chained Architecture (<800 ms Target)

```
Caller (8 kHz μ-law PSTN / Twilio Media Stream)
   │  resample 8 kHz → 16 kHz + acoustic VAD / semantic turn detector
   ▼
[1. Streaming STT]      NVIDIA Parakeet TDT 0.6B v2/v3 (or Qwen3-ASR / Gemma 4 audio-IN)
   │  partial + eager end-of-turn transcript
   ▼
[2. Fine-tuned Brain]   vLLM serving merged Gemma 4 E4B/12B (spoken register + tools + MTP drafter)
   │  token stream (clause-buffered, zero markdown)
   ▼
[3. Cloned Voice TTS]   WebSocket streaming Qwen3-TTS / Chatterbox-Turbo (LoRA cloned speaker)
   │  24 kHz PCM → downsample to 8 kHz μ-law + barge-in flush (<200 ms)
   ▼
Caller's Ear (reconciling text_spoken vs. text_remaining on every interrupt)
```

## 2. Orchestration Choice: Pipecat vs. LiveKit Agents
- **Pipecat (Python frame pipeline):** clean frame-by-frame control over VAD, Smart Turn Detection, custom vLLM/TTS services, per-stage TTFB metrics, and Twilio WebSockets.
- **LiveKit Agents (WebRTC + SIP):** battle-tested production WebRTC/SIP media routing, echo cancellation, and built-in scaling across rooms.

## 3. Live Phone Call Acceptance Checklist
Call your agent from a **real mobile phone** (including one call with background cafe/street noise) and verify:
1. **Per-stage p50 / p95 telemetry logged:** Ingress + VAD/Turn + STT + LLM TTFT + TTS TTFA < **800 ms** median.
2. **Mid-sentence barge-in test:** Interrupt the agent halfway through reading a confirmation number. Verify playback stops within `<200 ms`, no orphaned words leak into the next reply, and the agent's memory contains only `text_spoken`.
3. **Tool-calling test:** Trigger a live booking/lookup tool mid-call, confirm spoken filler/acknowledgement if tool latency >400 ms, and verify exact argument accuracy on spoken phone numbers and dates.
4. **Teardown:** Save recordings, latency span JSON, and cost-per-minute calculation to your Capstone Journal before stopping the GPU instances.
