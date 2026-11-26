"""Chat-turn formatting & completion-only loss masking (-100).

Topic: 04.04

One of the sneakiest silent bugs in fine-tuning is computing cross-entropy loss
over system instructions, user prompts, padding, or Gemma 4 audio soft tokens.
PyTorch ignores any label equal to -100.

Implement both single-completion masking (matching gemma.ai's audio/vision SFT
collator) and multi-turn assistant masking, plus a sanity-check stats helper.

Say it out loud:
  1. Why do we mask prompt and audio soft tokens to -100 instead of deleting
     them from input_ids?
  2. Why MUST the assistant's closing turn_end_id (<turn|>) stay unmasked?
  3. What happens if your collator fails to find assistant_prefix and leaves
     labels unmasked by accident?
"""
from __future__ import annotations


def build_completion_labels(
    input_ids: list[int],
    assistant_prefix: list[int],
    pad_token_id: int,
    ignored_token_ids: set[int] | None = None,
) -> list[int]:
    """Return a NEW list of labels matching input_ids where:
      - Every token up to and including the LAST occurrence of assistant_prefix
        is set to -100.
      - Every pad_token_id and every token in ignored_token_ids is set to -100.
      - If assistant_prefix is empty or not found in input_ids, the entire
        returned list is -100 (never silently train on an unparsed prompt!).
      - input_ids must NOT be mutated.
    """
    raise NotImplementedError


def build_multi_turn_labels(
    input_ids: list[int],
    assistant_prefix: list[int],
    turn_end_id: int,
    pad_token_id: int,
    ignored_token_ids: set[int] | None = None,
) -> list[int]:
    """Return a NEW list of labels supervising EVERY assistant turn:
      - Outside assistant turns (system, user, prefixes), label is -100.
      - After each occurrence of assistant_prefix, supervise every token up to
        and including the next turn_end_id (or end of sequence if truncated).
      - Always mask pad_token_id and ignored_token_ids to -100 even inside a turn.
      - If assistant_prefix is empty, return all -100.
      - input_ids must NOT be mutated.
    """
    raise NotImplementedError


def masked_token_stats(labels: list[int]) -> dict[str, float]:
    """Return {'total': int, 'supervised': int, 'masked': int, 'supervised_ratio': float}.

    For an empty list, supervised_ratio is 0.0.
    """
    raise NotImplementedError
