# §05 Inference Physics, Quantization & Serving

> Stage 4: build 4-bit block quantization and a KV cache from scratch before serving merged Gemma 4 on vLLM & SGLang with MTP speculative decoding and load tests.

Open `index.html` in this folder for the interactive dashboard.

## Topics

- [ ] `05.01` **[P0]** **Bits & quantization from scratch (BF16 → FP8 → 4-bit QAT)** — Implementing 4-bit block quantization, measuring rounding error, why Gemma 4's official QAT checkpoints beat PTQ, and why NF4 hurts audio & MoE routing.
- [ ] `05.02` **[P0]** **Prefill vs. decode & rebuilding the KV cache from scratch** — Adding a KV cache to your toy Transformer (O(N²) → O(N)), and tying decode tokens/sec straight back to GPU memory bandwidth.
- [ ] `05.03` **[P0]** **Continuous batching, PagedAttention, vLLM & SGLang** — Merging vs. multi-LoRA, fixing multimodal LoRA key-mapping gotchas, MTP speculative decoding, constrained JSON schemas, and concurrency load testing (TTFT/ITL).
- [ ] `05.04` **[P2]** **EmbeddingGemma & hybrid RAG + fine-tuned chains** — Fine-tuning domain retrieval embeddings with EmbeddingGemma and chaining live retrieval with a fine-tuned Gemma 4 generator.
- [ ] `05.05` **[P2]** **Specialist chains: FunctionGemma & ShieldGemma** — Putting tiny specialist models in front of and behind your main model for fast tool routing and low-latency safety/policy guardrails.
