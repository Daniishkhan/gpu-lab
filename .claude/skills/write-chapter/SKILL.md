---
name: write-chapter
description: Write or rewrite a gpu-lab book chapter in visual, analogy-first style with quick checks, real Gemma 4 / voice engineering numbers, and linked CPU exercises or GPU runbooks.
---

# Write a `gpu/lab` chapter

Goal: after one read top to bottom, Danish feels *why* an architecture,
fine-tuning technique, or voice-pipeline design exists, holds a crystal-clear
visual mental model, spots the real production gotchas missing from vendor docs
(`gemma.ai`), and is ready to code the CPU exercise or run the cloud GPU lab.

## 1. Blueprint first (before any HTML)
1. Check `curriculum.json` for `id`, `tag`, `requires`, and stage position.
   Never lean on a topic later in the track.
2. **Pain + payoff:** concrete OOM, latency, cost, or quality failure with real
   numbers + what Capstone 1 or Capstone 2 unlocks.
3. **One running physical analogy:** carried through the rebuild, naming where
   it breaks.
4. **Canonical flow:**
   - Plain-English header, intro, `.learn-list` (zero unintroduced jargon).
   - `s1`: Why do we even need this? (`.story` + early visual + payoff).
   - `s2..sN`: Question-led rebuild (`Question → Naive → Break → Fix`).
   - Production gotchas (`gemma.ai` gaps, failure modes, when NOT to use this).
   - How you use this in Capstone 1 / Capstone 2 (concrete before/after).
   - `#summary`, `#review`, `#exercises`, `chapter-nav`.
5. **Scope & visual pacing:** ~2,000–3,500 visible words, 5–8 quick checks
   (testing predictions, not trivia), early visual in s1–s2, max 2 consecutive
   sections without a visual. Put heavy math or secondary architectures in
   collapsed `details.aside.deeper`.

## 2. Hard technical rules
- Use `"gpu-lab:"` in the inline theme snippet.
- Offline only (zero CDNs, zero `fetch()`, theme CSS variables only).
- Remove `<meta name="status" content="outline">` once complete.
- Run `python3 tools/build.py` and verify any linked CPU exercises with
  `tools/check_exercise.py` (keeping reference solutions in a temporary scratch
  folder outside the repo, then deleting them).
- Hand off to `visuals-and-layout`, then `review-chapter`.
