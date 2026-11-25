# §03 Inventing the Transformer → Gemma 4

> Stage 2: invent tokenization, Q/K/V causal attention, and a ~120-line toy GPT from scratch — then map every single line 1-to-1 onto Gemma 4's four production architectures.

Open `index.html` in this folder for the interactive dashboard.

## Topics

- [ ] `03.01` **[P0]** **From characters to tokens & embeddings** — Building Byte-Pair Encoding (BPE) from scratch, vocab size vs. sequence length trade-offs, and embedding lookup tables.
- [ ] `03.02` **[P0]** **The problem Attention solves: Q, K, V & RoPE** — Why averaging words loses order, inventing Query/Key/Value soft search-and-blend, causal masking, multi-head attention, and RoPE positional rotation.
- [ ] `03.03` **[P0]** **Build a 120-line toy Transformer & watch it learn** — Assembling residual highways, RMSNorm, attention, and SwiGLU MLP blocks into a runnable toy GPT and watching random noise turn into structured text.
- [ ] `03.04` **[P0]** **Inside Gemma 4's four architectures** — Mapping your toy GPT onto Gemma 4: GQA, PLE (E2B/E4B), unified encoder-free 12B, 128-expert MoE (26B-A4B), dense 31B, MTP drafters, and base vs. -it.
