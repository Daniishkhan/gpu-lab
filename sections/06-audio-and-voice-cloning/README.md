# §06 Sound Waves, Codecs & Voice Cloning

> Stage 5: from air pressure waves and 8 kHz phone physics to RVQ audio codecs, zero-shot + LoRA voice cloning (Qwen3-TTS, Chatterbox, Orpheus), and <150 ms streaming TTS.

Open `index.html` in this folder for the interactive dashboard.

## Topics

- [ ] `06.01` **[P0]** **Air pressure to numbers: waveforms, FFT & 8 kHz phone physics** — PCM sample rates (8 kHz μ-law PSTN vs. 16/24 kHz), Nyquist limit, FFT, log-mel spectrograms from scratch, and simulating phone-line degradation.
- [ ] `06.02` **[P0]** **How neural networks hear speech** — 40 ms audio windows (25 soft tokens/sec), Conformer encoders (Gemma 4 E2B/E4B, Parakeet) vs. encoder-free linear stems (Gemma 4 12B), and the audio-IN / text-OUT boundary.
- [ ] `06.03` **[P0]** **How neural networks speak: RVQ codecs & vocoders** — Why raw 24 kHz waveforms break Transformers, building a tiny Residual Vector Quantizer (Mimi / Qwen3-TTS 12 Hz concept), semantic vs. acoustic tokens, and vocoders.
- [ ] `06.04` **[P0]** **Voice hygiene, zero-shot cloning & speaker LoRA** — VAD/SNR/dereverb/alignment/consent; 3-second zero-shot cloning vs. LoRA speaker fine-tuning on Qwen3-TTS (Apache 2.0), Chatterbox-Turbo (MIT), and Orpheus TTS.
- [ ] `06.05` **[P0]** **Streaming TTS & naturalness (<150 ms TTFA)** — Dual-track streaming synthesis, clause chunking, spoken normalization (numbers, dates, currency), WebSocket serving, speaker similarity, and 8 kHz round-trip WER evals.
- [ ] `06.06` **[P2]** **Consent, codec-surviving watermarks & caller disclosure** — Responsible voice cloning controls: speaker consent verification, watermarks surviving 8 kHz telephony codecs, and caller disclosure UX.
