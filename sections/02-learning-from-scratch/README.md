# §02 Neural Nets & Backprop From Scratch

> Stage 1: build gradient descent, a 40-line autograd engine, and a tiny next-character predictor in pure Python before touching PyTorch — so nothing feels like magic.

Open `index.html` in this folder for the interactive dashboard.

## Topics

- [ ] `02.01` **[P0]** **Guess, measure wrongness, nudge downhill** — Fitting y = w*x + b to 4 points: loss functions, numerical & analytic slopes (gradients), learning rate stability, and gradient descent.
- [ ] `02.02` **[P0]** **Backpropagation from scratch (micro-autograd)** — The chain rule as local blame assignment through a computation graph — building a 40-line scalar Value autograd engine in pure Python.
- [ ] `02.03` **[P0]** **Bending straight lines: MLPs, activations & softmax** — Why linear layers collapse without nonlinearities, ReLU/GELU/SwiGLU, turning logits into probabilities (softmax), and cross-entropy loss on a tiny next-char LM.
- [ ] `02.04` **[P0]** **Peeling off the training wheels: PyTorch & Hugging Face** — Mapping every line of your pure-Python engine onto torch.Tensor, .backward(), nn.Module, AdamW, .to('cuda'), and Hugging Face AutoTokenizer / AutoModel.
