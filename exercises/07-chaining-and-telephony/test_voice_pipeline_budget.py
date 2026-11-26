import pytest

from voice_pipeline_budget import (
    apply_turn_event,
    mouth_to_ear_ms,
    reconcile_barge_in,
)


def test_mouth_to_ear_budget_and_overlap():
    plain = mouth_to_ear_ms(60, 320, 120, 250, 95)
    assert plain["total_ms"] == 845
    assert plain["within_target"] is False
    assert plain["headroom_ms"] == -45
    assert plain["bottleneck"] == "endpointing"

    # Speculative prefill overlaps 160 ms with endpointing + STT -> drops under 800 ms!
    spec = mouth_to_ear_ms(60, 320, 120, 250, 95, speculative_prefill_overlap_ms=160)
    assert spec["effective_llm_ms"] == 90
    assert spec["total_ms"] == 685
    assert spec["within_target"] is True
    assert spec["headroom_ms"] == 115

    # Overlap cannot exceed endpointing + stt_finalize or make LLM negative
    capped = mouth_to_ear_ms(50, 100, 50, 120, 80, speculative_prefill_overlap_ms=500)
    assert capped["effective_llm_ms"] == 0
    assert capped["total_ms"] == 280


def test_mouth_to_ear_validation():
    with pytest.raises(ValueError):
        mouth_to_ear_ms(-1, 200, 100, 200, 90)
    with pytest.raises(ValueError):
        mouth_to_ear_ms(50, 200, 100, 200, 90, target_ms=0)


def test_reconcile_barge_in_with_word_timings():
    timings = [
        ("The", 0, 120),
        ("pool", 120, 340),
        ("opens", 340, 620),
        ("at", 620, 760),
        ("six.", 760, 1050),
    ]
    spoken, rem = reconcile_barge_in("The pool opens at six.", 1050, 600, timings)
    assert spoken == "The pool opens"
    assert rem == "at six."

    assert reconcile_barge_in("The pool opens at six.", 1050, 0, timings) == ("", "The pool opens at six.")
    assert reconcile_barge_in("The pool opens at six.", 1050, 1200, timings) == ("The pool opens at six.", "")


def test_reconcile_barge_in_proportional_fallback():
    spoken, rem = reconcile_barge_in("One two three four", 1000, 500)
    assert spoken == "One two"
    assert rem == "three four"
    with pytest.raises(ValueError):
        reconcile_barge_in("Hello", 0, 100)


def test_turn_event_state_machine_and_barge_in():
    s0 = {"phase": "listening", "speculative_llm_calls": 0, "history": [], "active_tts": None}
    s1 = apply_turn_event(s0, {"type": "EagerEndOfTurn"})
    assert s0["phase"] == "listening" and s0["speculative_llm_calls"] == 0
    assert s1["phase"] == "speculating" and s1["speculative_llm_calls"] == 1

    # Caller kept talking -> cancel speculative draft
    s2 = apply_turn_event(s1, {"type": "TurnResumed"})
    assert s2["phase"] == "listening" and s2["speculative_llm_calls"] == 1

    # Caller finishes -> agent starts speaking
    s3 = apply_turn_event(s2, {
        "type": "EndOfTurn",
        "transcript": "When does the pool open?",
        "reply_text": "The pool opens at six.",
        "reply_audio_ms": 1050,
    })
    assert s3["phase"] == "speaking"
    assert s3["history"] == [("user", "When does the pool open?")]
    assert s2["history"] == []

    # Caller interrupts at 600 ms -> only spoken words enter history!
    timings = [("The", 0, 120), ("pool", 120, 340), ("opens", 340, 620), ("at", 620, 760), ("six.", 760, 1050)]
    s4 = apply_turn_event(s3, {"type": "BargeIn", "played_ms": 600, "word_timings_ms": timings})
    assert s4["phase"] == "listening"
    assert s4["active_tts"] is None
    assert s4["history"] == [
        ("user", "When does the pool open?"),
        ("assistant", "The pool opens"),
    ]
    assert len(s3["history"]) == 1, "previous state history must not be mutated"
