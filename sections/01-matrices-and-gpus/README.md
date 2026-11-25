# §01 Matrices, NumPy & GPU Hardware

> Phase 0: assumes only basic Python fluency (use swe-lab for core Python). Builds exact physical intuition for dot products, batched matrix shapes, and GPU compute vs. memory bandwidth.

Open `index.html` in this folder for the interactive dashboard.

## Topics

- [ ] `01.01` **[P0]** **From Python loops to vectors & dot products** — Why ML encodes words, sounds, and weights as vectors, why dot products measure alignment, and replacing Python loops with NumPy vectorization.
- [ ] `01.02` **[P0]** **Matrix multiplication & shapes for ML** — Why every neural layer is a matrix multiply (@), batching (B, T, D), broadcasting, transposes, and debugging tensor shapes without guessing.
- [ ] `01.03` **[P0]** **What is a GPU and why do we need one?** — CPU vs. GPU parallelism, FLOPs vs. memory bandwidth, VRAM vs. system RAM, arithmetic intensity, and why prefill loves GPUs while decode starves them.
