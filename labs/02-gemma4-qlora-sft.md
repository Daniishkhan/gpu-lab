# Lab 02 · Fine-Tuning Gemma 4 (Text SFT) + Merge Parity Check

- **Topic:** `04.05` (Stage 3 · Capstone 1)
- **Recommended GPU:** `1× NVIDIA L4 (24 GB)` (QLoRA on `E4B-it` or `12B-it`; BF16 LoRA on `E4B-it`)
- **Estimated VRAM / Runtime / Cost:** `~9–14 GB` · `~25–45 min` · `~$0.40–$0.60`

## Pre-Flight Checks (do locally first)
- [ ] Pass `python3 -m pytest -k "loss_masking or lora_math"`
- [ ] Have your Capstone 1 `train.jsonl`, `val.jsonl`, and held-out `test.jsonl` ready
- [ ] Measure **greedy (`do_sample=False`) baseline score** on `test.jsonl` BEFORE training

## 1. Environment Setup

```bash
pip install -U "transformers>=5.10.1" "trl>=0.16.0" "peft>=0.19.0" \
               "accelerate>=1.4.0" "datasets" "bitsandbytes"
# Optional single-GPU speed-up (2x faster QLoRA & clean GGUF export):
# pip install unsloth
```

## 2. Production Gotchas Built Into This Recipe
1. **Pin `transformers>=5.10.1` & `peft>=0.19.0`:** older versions broke on Gemma 4's `ClippableLinear` wrapper and `use_cache=False` KV-sharing gradients.
2. **Explicit `-100` completion-only masking:** mask everything before `<|turn>model\n` AND pad tokens so gradients only flow from your target output.
3. **Skip DeepSpeed ZeRO-3 for LoRA:** ZeRO-3 can save half-empty adapters; use single-GPU or FSDP2 instead.
4. **Always verify merged parity:** before deploying to `vLLM` or `SGLang`, run `merge_and_unload()` and verify greedy outputs match the PEFT eval model on 10 test prompts.

## 3. Training Skeleton (TRL + PEFT QLoRA on 1× L4)

```python
import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForMultimodalLM, AutoProcessor, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

MODEL_ID = "google/gemma-4-E4B-it"  # swap to google/gemma-4-12B-it once pipeline is clean
bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForMultimodalLM.from_pretrained(
    MODEL_ID, quantization_config=bnb, device_map="cuda"
)

peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    exclude_modules=r"model\.(vision_tower|audio_tower)\..*",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()

# Reuse the exact completion-only masking logic you verified in loss_masking.py!
# After training:
#   trainer.save_model("out/adapter")
#   Reload BF16 base + PeftModel -> merge_and_unload() -> save_pretrained("out/merged")
```

## 4. Merge & Serve Sanity Check (Week 4 Preview)
1. Reload the BF16 base checkpoint + your saved LoRA adapter, run your held-out `test.jsonl` greedy eval, and record the before → after delta.
2. Call `merged = peft_model.merge_and_unload()`, save to `out/merged`, and re-run 10 prompts via `vLLM` (`vllm serve out/merged`).
3. Confirm outputs match (catching any silent vLLM adapter-ignored or template-drift bug!).
4. Log results in `workbench.html` and shut down the GPU pod.
