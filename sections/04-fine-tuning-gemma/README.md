# §04 Fine-Tuning Gemma 4 (Text Capstone 1)

> Stage 3: exact VRAM math, LoRA from scratch, closing gemma.ai's data/eval/masking gaps, single-GPU SFT, debugging runs, and post-training RL (DPO & GRPO).

Open `index.html` in this folder for the interactive dashboard.

## Topics

- [ ] `04.01` **[P0]** **Where does all the GPU memory go?** — Exact byte accounting for weights, gradients, AdamW vs. 8-bit optimizer states, activations (gradient checkpointing), KV cache, and Gemma 4 PLE/MoE quirks.
- [ ] `04.02` **[P0]** **LoRA & QLoRA from scratch** — Low-rank steering y = W@x + (alpha/r)*B@(A@x), zero-init B=0 invariant, rank/alpha scaling, target modules, and exact weight merging W + (alpha/r)*(B@A).
- [ ] `04.03` **[P0]** **Before you train: when NOT to fine-tune, datasets & evals** — Prompt vs. RAG vs. SFT vs. RL decision matrix, golden eval harnesses BEFORE renting GPUs, curating real examples, and 31B → E4B/12B distillation.
- [ ] `04.04` **[P0]** **Chat templates & -100 completion-only loss masking** — Gemma 4 turn markers (<|turn>user, <|turn>model, <turn|>, thinking channel), masking prompt/pad/audio tokens to -100, and preventing train-serve drift.
- [ ] `04.05` **[P0]** **Fine-tuning Gemma 4 (SFT) & debugging runs** — Running QLoRA/BF16 LoRA with TRL, PEFT & Unsloth, Gemma 4 gotchas (ClippableLinear, use_cache, NF4 vs. BF16, ZeRO-3), reading loss curves, and fixing forgetting.
- [ ] `04.06` **[P1]** **Beyond imitation: DPO & GRPO verifiable rewards** — Shaping tone/conciseness via preference pairs (DPO) and boosting strict JSON/SQL/code/tool accuracy via pass/fail verifiable reward functions (GRPO).
- [ ] `04.07` **[P2]** **MoE fine-tuning on Gemma 4 26B-A4B** — Adapting 128 routed experts with Split-LoRA while keeping the router frozen, preventing expert collapse, and avoiding 4-bit routing drift.
- [ ] `04.08` **[P2]** **Continued pre-training & custom tokens** — Starting from raw pre-trained checkpoints for deep domain corpora with sequence packing, 10% replay buffers, custom templates, and reserved token slots.
- [ ] `04.09` **[P2]** **Teacher-student distillation (31B → E2B/E4B)** — Generating verified reasoning and task traces from Gemma 4 31B and distilling them into fast, cheap edge/L4 checkpoints.
