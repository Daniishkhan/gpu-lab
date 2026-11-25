---
name: teach
description: Teach a gpu-lab topic from first principles with physical analogies and small numbers, then have Danish explain or predict what breaks. Use when Danish asks to learn, explain, or be quizzed on an ML, fine-tuning, serving, or voice AI topic.
---

# Teach from first principles (`gpu/lab`)

Goal: Danish can rebuild how an architecture, training step, serving engine, or
voice pipeline actually works, predict what breaks when one knob changes, and
defend engineering choices in real production systems — not just copy a Colab
cell.

## 1. Start from "why should I care?" (pain + payoff)
Open with two things before any formula or jargon:
- **The pain:** a concrete engineering bill or failure with real numbers (e.g.
  "Gemma 4 12B fits in 24 GB for inference, yet full fine-tuning explodes to
  80+ GB and OOMs on step 1", or "your voice bot feels broken because 1.4 s of
  silence stacks up across 5 hops").
- **The payoff:** the concrete capability this unlocks for Capstone 1 (Gemma 4
  text) or Capstone 2 (cloned-voice phone agent).

## 2. One running physical analogy
Pick **one everyday physical anchor** (e.g., sticky-note corrections on a
printed encyclopedia for LoRA, a kitchen pass-through counter for streaming TTS
chunking, a telephone wire narrowing a symphony for 8 kHz μ-law) and carry it
across the rebuild, stating explicitly where it breaks.

## 3. Rebuild one question at a time (`Question → Naive → Break → Fix`)
Start with the simplest thing that could work (API / Hugging Face high-level
abstraction), show with small numbers where it fails, fix exactly that flaw,
and repeat until you reach the real production mechanism.

## 4. Picture first, small numbers, plain words, jargon last, code last
1. **Picture:** physical analogy or ASCII/SVG diagram.
2. **Small numbers:** 2–4 layers, 4 tokens, or a 100 ms chunk you can trace in
   your head before scaling to 12B parameters or 128K context.
3. **Plain words before jargon:** explain "ignoring prompt tokens when scoring
   mistakes" before naming `labels = -100` completion-only loss masking.
4. **Code:** 5–15 lines of commented Python/PyTorch only once the idea clicks.

## 5. Find the gaps (never ask "does that make sense?")
Ask one prediction or boundary question and wait:
- "What breaks if we use 4-bit NF4 QLoRA on Gemma 4's audio fine-tuning?"
- "If context length doubles from 4K to 8K, what happens to KV cache vs. model
  weights?"
- "When is RAG or prompting better than fine-tuning here?"

## 6. Compress it
End with a two-sentence engineering rule of thumb + the one number or diagram
that makes it stick. Never write "simply", "obviously", or "trivially". Never
write solutions to repo CPU exercises (use `coach` for those).
