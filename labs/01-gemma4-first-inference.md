# Lab 01 · First Gemma 4 Cloud GPU Run & Profiling

- **Topic:** `03.04` (Stage 2)
- **Recommended GPU:** `1× NVIDIA L4 (24 GB)` on RunPod, Modal, Lambda, or Colab Pro
- **Estimated VRAM / Runtime / Cost:** `~18 GB (BF16)` or `~6 GB (Q4)` · `~20 min` · `~$0.25`

## Pre-Flight Checks (do locally first)
- [ ] Read `sections/01-matrices-and-gpus/concepts/what-is-a-gpu.html` and Stage 2 chapters`
- [ ] Pass `python3 -m pytest -k gpu_roofline`
- [ ] Have a Hugging Face account & read token (`HF_TOKEN`) ready

## 1. Environment Setup (pinned Gemma 4 versions)

```bash
pip install -U "transformers>=5.10.1" "accelerate>=1.4.0" "bitsandbytes" "safetensors"
export HF_TOKEN="hf_your_token_here"
```

## 2. Profile Base vs. `-it`, TTFT, Decode Speed & Peak VRAM

Save and run `profile_gemma4.py` on your L4:

```python
import time
import torch
from transformers import AutoModelForMultimodalLM, AutoProcessor

MODEL_ID = "google/gemma-4-E4B-it"
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForMultimodalLM.from_pretrained(
    MODEL_ID, dtype=torch.bfloat16, device_map="cuda"
)
model.eval()
print(f"Loaded VRAM: {torch.cuda.max_memory_allocated() / 1e9:.2f} GB")

messages = [
    {"role": "system", "content": "Reply in one concise spoken sentence. No markdown."},
    {"role": "user", "content": "Explain why GPU memory matters when fine-tuning a model."},
]
prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = processor(text=[prompt], return_tensors="pt").to("cuda")

stop_ids = [
    processor.tokenizer.eos_token_id,
    processor.tokenizer.convert_tokens_to_ids("<turn|>"),
]

# Warm up CUDA kernels
with torch.no_grad():
    _ = model.generate(**inputs, max_new_tokens=8, do_sample=False, eos_token_id=stop_ids)
torch.cuda.synchronize()

t0 = time.perf_counter()
with torch.no_grad():
    out = model.generate(**inputs, max_new_tokens=80, do_sample=False, eos_token_id=stop_ids)
torch.cuda.synchronize()
elapsed = time.perf_counter() - t0

gen_ids = out[0][inputs.input_ids.shape[1]:]
text = processor.tokenizer.decode(gen_ids, skip_special_tokens=True)
print(f"\nReply ({len(gen_ids)} tokens in {elapsed:.2f}s = {len(gen_ids)/elapsed:.1f} tok/s):\n{text}")
print(f"Peak VRAM: {torch.cuda.max_memory_allocated() / 1e9:.2f} GB")
```

## 3. What to Observe & Log in `workbench.html`
1. Compare your measured `Peak VRAM` against your `gpu_roofline.py` prediction.
2. Inspect the exact `prompt` string printed with special tokens visible — notice `<|turn>system`, `<|turn>user`, `<turn|>`, and `<|turn>model`.
3. Remove `processor.tokenizer.convert_tokens_to_ids("<turn|>")` from `stop_ids` once and watch what happens!
4. Log your baseline speed and VRAM in `workbench.html` → Experiment Run Log, then **shut down the GPU pod**.
