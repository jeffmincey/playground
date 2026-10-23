"""Checks for the multi-module DBC generator (standard library only)."""

import re

from gen_dbc import SOURCE, STRIDE, generate


def frame_ids(text):
    return [int(m) for m in re.findall(r"^BO_ (\d+) ", text, re.M)]


def test_two_modules_repeat_every_frame_at_the_next_address():
    src = SOURCE.read_text()
    base = frame_ids(src)
    out = generate(src, 2)
    assert sorted(frame_ids(out)) == sorted(base + [i + STRIDE for i in base])
    assert len(set(frame_ids(out))) == 2 * len(base)


def test_nodes_and_names_follow_the_address():
    out = generate(SOURCE.read_text(), 2)
    assert "BU_: HOST PCM0 PCM1" in out
    assert "PCM1_Command" in out and "PCM1_Status" in out
    assert f"VAL_ {0x6A0 + STRIDE} OUT1_Req" in out


def test_generated_file_is_current():
    from pathlib import Path

    committed = Path(SOURCE).with_name("pcm-jk.dbc").read_text()
    assert committed == generate(SOURCE.read_text(), 2), "re-run tools/gen_dbc.py"
