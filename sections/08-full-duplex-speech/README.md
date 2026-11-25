# §08 Native Full-Duplex Speech-to-Speech

> Stage 7A: single-network listen-while-speaking models (Moshi, NVIDIA PersonaPlex 7B, NemotronLabs VoiceChat 11B) — fine-tuned on stereo audio and benchmarked honestly vs. your Stage 6 cascade.

Open `index.html` in this folder for the interactive dashboard.

## Topics

- [ ] `08.01` **[P1]** **Native full-duplex S2S (Moshi, PersonaPlex & VoiceChat)** — Dual-stream listen-and-speak over Mimi codec tokens, inner text monologue, PersonaPlex 7B voice/role conditioning, and NemotronLabs VoiceChat 11B mid-call tool tokens.
- [ ] `08.02` **[P1]** **Fine-tuning full-duplex models & cascade head-to-head** — Stereo LoRA fine-tuning (moshi-finetune) and honest head-to-head comparison against Stage 6 on dynamics, spoken reasoning, tool accuracy, 8 kHz audio, and calls per H100.
