"""Voice agent latency budget (<800 ms) & Deepgram-Flux-style barge-in reconciliation.

Topic: 07.02, 07.03

Why do great voice agents feel snappy and duplex even when built as a cascade?
  1. They budget every hop against the ~800 ms noticeable-lag ceiling and
     overlap speculative LLM prefill with turn finalization.
  2. On mid-sentence caller interruption (barge-in), they immediately flush
     queued TTS audio AND reconcile the exact text_spoken vs. text_remaining
     in conversation history so orphaned words never leak into the next turn.

Say it out loud:
  1. Why does speculative LLM prefill on EagerEndOfTurn trade cheap tokens for
     100-200 ms of perceived responsiveness?
  2. What user-visible bug happens if a caller interrupts mid-sentence and you
     commit the LLM's entire generated text instead of text_spoken?
"""
from __future__ import annotations


def mouth_to_ear_ms(
    ingress_jitter_ms: int,
    endpointing_ms: int,
    stt_finalize_ms: int,
    llm_ttft_ms: int,
    tts_ttfa_ms: int,
    speculative_prefill_overlap_ms: int = 0,
    target_ms: int = 800,
) -> dict[str, object]:
    """Compute effective mouth-to-ear latency and stage bottleneck.

    Speculative prefill overlaps LLM prefill with endpointing + STT finalization,
    so the effective LLM wait is:
        effective_llm = max(0, llm_ttft_ms - min(speculative_prefill_overlap_ms,
                                                 endpointing_ms + stt_finalize_ms))

    Return a dict with:
      - 'effective_llm_ms': int
      - 'total_ms': int (sum of ingress_jitter, endpointing, stt_finalize,
                         effective_llm, tts_ttfa)
      - 'within_target': bool (total_ms <= target_ms)
      - 'headroom_ms': int (target_ms - total_ms)
      - 'bottleneck': str (one of 'ingress_jitter', 'endpointing', 'stt_finalize',
                           'llm_ttft', 'tts_ttfa'; use effective_llm for 'llm_ttft',
                           tie-break by earlier stage in that list)

    Raise ValueError if any latency input is negative or target_ms <= 0.
    """
    raise NotImplementedError


def reconcile_barge_in(
    full_text: str,
    total_audio_ms: int,
    played_audio_ms: int,
    word_timings_ms: list[tuple[str, int, int]] | None = None,
) -> tuple[str, str]:
    """Split full_text into (text_spoken, text_remaining) when interrupted at played_audio_ms.

    Rules:
      - If played_audio_ms <= 0: return ("", full_text.strip())
      - If played_audio_ms >= total_audio_ms: return (full_text.strip(), "")
      - If word_timings_ms is provided as [(word, start_ms, end_ms), ...]:
          A word counts as spoken if start_ms < played_audio_ms.
          Join spoken words with " " and remaining words with " ".
      - Otherwise (proportional fallback on full_text.split()):
          spoken_count = round(len(words) * played_audio_ms / total_audio_ms),
          clamped to [0, len(words)].
          Join words[:spoken_count] and words[spoken_count:] with " ".

    Raise ValueError if total_audio_ms <= 0.
    """
    raise NotImplementedError


def apply_turn_event(state: dict, event: dict) -> dict:
    """Return a NEW state dict after processing one streaming voice-agent event.

    State keys:
      - 'phase': 'listening' | 'speculating' | 'speaking'
      - 'speculative_llm_calls': int
      - 'history': list[tuple[str, str]]   # e.g. [('user', 'hi'), ('assistant', 'hello')]
      - 'active_tts': dict | None          # {'text': str, 'total_ms': int}

    Supported events (event['type']):
      - 'EagerEndOfTurn': sets phase='speculating', increments speculative_llm_calls by 1.
      - 'TurnResumed':    if phase == 'speculating', sets phase='listening' (cancels draft).
      - 'EndOfTurn':      appends ('user', event['transcript']) to history,
                          sets phase='speaking',
                          sets active_tts={'text': event['reply_text'], 'total_ms': event['reply_audio_ms']}.
      - 'TtsFinished':    if active_tts is present, appends ('assistant', active_tts['text'])
                          to history, sets active_tts=None, phase='listening'.
      - 'BargeIn':        if active_tts is present, uses reconcile_barge_in(
                          active_tts['text'], active_tts['total_ms'], event['played_ms'],
                          event.get('word_timings_ms')) to get (spoken, _remaining);
                          if spoken is non-empty, appends ('assistant', spoken) to history;
                          sets active_tts=None, phase='listening'.

    Must NOT mutate the input state or its history list.
    Raise ValueError on unknown event['type'].
    """
    raise NotImplementedError
