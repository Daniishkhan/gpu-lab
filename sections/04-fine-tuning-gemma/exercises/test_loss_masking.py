import pytest

from loss_masking import (
    build_completion_labels,
    build_multi_turn_labels,
    masked_token_stats,
)

# Synthetic Gemma-4-like token IDs
PAD = 0
USER_PRE = [10, 11]        # <|turn>user\n
MODEL_PRE = [10, 12]       # <|turn>model\n
TURN_END = 19              # <turn|>
AUDIO_IDS = {256000, 258881, 258883}


def test_single_turn_completion_and_audio_masking():
    ids = USER_PRE + [256000, 258881, 258883, 42, 43, TURN_END] + MODEL_PRE + [100, 101, TURN_END, PAD, PAD]
    snap = list(ids)
    labels = build_completion_labels(ids, MODEL_PRE, PAD, AUDIO_IDS)
    assert ids == snap, "input_ids must not be mutated"
    prefix_end = len(USER_PRE) + 6 + len(MODEL_PRE)
    assert labels[:prefix_end] == [-100] * prefix_end
    assert labels[prefix_end:] == [100, 101, TURN_END, -100, -100]


def test_completion_uses_last_assistant_prefix():
    ids = (
        USER_PRE + [1, TURN_END]
        + MODEL_PRE + [2, TURN_END]
        + USER_PRE + [3, TURN_END]
        + MODEL_PRE + [4, 5, TURN_END]
    )
    labels = build_completion_labels(ids, MODEL_PRE, PAD)
    # Only the final reply [4, 5, TURN_END] is supervised
    assert labels[:-3] == [-100] * (len(ids) - 3)
    assert labels[-3:] == [4, 5, TURN_END]


def test_missing_or_empty_prefix_masks_everything():
    ids = USER_PRE + [42, 43, TURN_END]
    assert build_completion_labels(ids, MODEL_PRE, PAD) == [-100] * len(ids)
    assert build_completion_labels(ids, [], PAD) == [-100] * len(ids)
    assert build_completion_labels([], MODEL_PRE, PAD) == []


def test_multi_turn_supervises_all_assistant_turns_including_stop():
    ids = (
        USER_PRE + [256000, 50, TURN_END]
        + MODEL_PRE + [60, 61, TURN_END]
        + USER_PRE + [70, TURN_END]
        + MODEL_PRE + [80, 258881, 81, TURN_END, PAD]
    )
    snap = list(ids)
    labels = build_multi_turn_labels(ids, MODEL_PRE, TURN_END, PAD, AUDIO_IDS)
    assert ids == snap
    expected = (
        [-100, -100, -100, -100, -100]
        + [-100, -100, 60, 61, TURN_END]
        + [-100, -100, -100, -100]
        + [-100, -100, 80, -100, 81, TURN_END, -100]
    )
    assert labels == expected


def test_multi_turn_truncated_final_turn():
    ids = USER_PRE + [1, TURN_END] + MODEL_PRE + [90, 91]
    labels = build_multi_turn_labels(ids, MODEL_PRE, TURN_END, PAD)
    assert labels == [-100, -100, -100, -100, -100, -100, 90, 91]


def test_masked_token_stats():
    stats = masked_token_stats([-100, -100, 10, 20, -100])
    assert stats["total"] == 5
    assert stats["supervised"] == 2
    assert stats["masked"] == 3
    assert stats["supervised_ratio"] == pytest.approx(0.4)

    empty = masked_token_stats([])
    assert empty == {"total": 0, "supervised": 0, "masked": 0, "supervised_ratio": 0.0}
