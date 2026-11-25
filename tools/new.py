#!/usr/bin/env python3
"""
Scaffold new gpu-lab material from templates/ and refresh assets/curriculum.js.

  python3 tools/new.py concept  01.01 vectors-and-dots  "From Python loops to vectors & dot products"
  python3 tools/new.py exercise 03.02 attention_scratch "Causal self-attention from scratch"
  python3 tools/new.py exp      "Gemma 4 E4B LoRA run 01"
  python3 tools/new.py eval     "Capstone 1 structured extraction"
  python3 tools/new.py runbook  "PersonaPlex stereo LoRA"
  python3 tools/new.py capstone "Cloned-voice booking phone agent"
"""
from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "templates"


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def topic(tid: str) -> tuple[dict, dict]:
    data = json.loads((ROOT / "curriculum.json").read_text())
    for sec in data["sections"]:
        for t in sec["topics"]:
            if t["id"] == tid:
                return sec, t
    sys.exit(f"Unknown topic id {tid}. See curriculum.json (ids look like 01.03).")


def fill(text: str, **kw) -> str:
    for k, v in kw.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def write(path: Path, text: str) -> None:
    if path.exists():
        sys.exit(f"{path.relative_to(ROOT)} already exists; not overwriting.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("created", path.relative_to(ROOT))


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        sys.exit(__doc__)
    kind = argv[0]
    today = dt.date.today().isoformat()
    if kind in ("concept", "exercise"):
        tid, name = argv[1], argv[2]
        title = argv[3] if len(argv) > 3 else name.replace("_", " ").replace("-", " ").capitalize()
        sec, t = topic(tid)
        d = ROOT / "sections" / sec["slug"]
        kw = dict(TITLE=title, TOPIC_ID=tid, TAG=t["tag"], TOPIC_TEXT=t["text"],
                  SECTION_ID=sec["id"], SECTION_TITLE=sec["title"])
        if kind == "concept":
            write(d / "concepts" / f"{slugify(name)}.html", fill((T / "concept.html").read_text(), **kw))
        else:
            mod = re.sub(r"\W", "_", name)
            if list(ROOT.glob(f"sections/*/exercises/{mod}.py")):
                sys.exit(f"An exercise module named {mod} already exists; pick a unique name.")
            write(d / "exercises" / f"{mod}.py", fill((T / "exercise.py").read_text(), MODULE=mod, **kw))
            write(d / "exercises" / f"test_{mod}.py", fill((T / "test_exercise.py").read_text(), MODULE=mod))
    elif kind in ("exp", "eval", "runbook", "capstone"):
        title = argv[1]
        where, tpl = {
            "exp": ("sections/09-production-and-capstones/experiments", "experiment-log.md"),
            "eval": ("sections/04-fine-tuning-gemma/eval-specs", "eval-spec.md"),
            "runbook": ("labs", "gpu-runbook.md"),
            "capstone": ("sections/09-production-and-capstones/capstones", "capstone-plan.md"),
        }[kind]
        write(ROOT / where / f"{slugify(title)}.md", fill((T / tpl).read_text(), TITLE=title, DATE=today))
    else:
        sys.exit(__doc__)
    subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], check=False)


if __name__ == "__main__":
    main(sys.argv[1:])
