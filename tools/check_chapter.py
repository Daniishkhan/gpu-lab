#!/usr/bin/env python3
"""
Zero-dependency offline quality linter for gpu/lab HTML book chapters.

Usage:
  python3 tools/check_chapter.py book/sections/01-matrices-and-gpus/concepts/what-is-a-gpu.html
  python3 tools/check_chapter.py --all
  python3 tools/check_chapter.py --all --strict

Checks (without needing Playwright):
  - Metadata & offline rules: valid topic ID in curriculum.json, "gpu-lab:theme",
    no external script/css/img URLs, no fetch(), no broken local links.
  - Markup integrity: no duplicate IDs, every main h2 has an id, every .check
    has check-* id + 1 data-correct + .fb.right + .fb.wrong, every .figure has
    .cap, every table sits in .table-wrap.
  - Theme safety: no hardcoded hex/rgb/hsl colors in SVG attributes or style="".
  - Prose hygiene: no raw Markdown (`backticks`, **bold**) or unescaped <|turn>
    tokens in HTML prose; warns on patronizing filler ("simply", "obviously"...).
  - First-principles pacing (complete chapters): #summary, #review, .learn-list,
    .chapter-nav, early visual in s1–s2, max 2 consecutive numbered sections
    without a visual, word count (~2,000–3,500), and quick-check count (5–8).

Exits 1 if any errors are found (or warnings under --strict).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEX_OR_FUNC_COLOR = re.compile(r"(?:#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\s*\()", re.I)
RAW_BACKTICKS = re.compile(r"`[^`\n]{1,120}`")
RAW_MD_BOLD = re.compile(r"\*\*[^*\n]{2,80}\*\*")
UNESCAPED_TURN = re.compile(r"<\|?turn\|?>", re.I)
ANTI_SLOP = re.compile(
    r"\b(?:simply|obviously|trivially|it\s+is\s+easy\s+to\s+see|delve\s+into|unlock\s+the\s+power\s+of)\b",
    re.I,
)
SVG_COLOR_ATTRS = {"fill", "stroke", "color", "stop-color"}
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class ChapterParser(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.path = path
        self.stack: list[dict] = []
        self.meta: dict[str, str] = {}
        self.has_title = False
        self.has_main_book = False
        self.ids: dict[str, int] = {}
        self.main_h2_missing_id: list[str] = []
        self.external_assets: list[str] = []
        self.local_links: list[tuple[str, str]] = []
        self.hardcoded_colors: list[str] = []
        self.tables_unwrapped = 0
        self.checks: list[dict] = []
        self.figures: list[dict] = []
        self.scripts: list[str] = []
        self.prose_chunks: list[str] = []
        self.core_words_chunks: list[str] = []
        self.has_learn_list = False
        self.has_chapter_nav = False
        self.sections: list[dict] = []  # numbered h2 sections (#s1, #s2, ...)
        self.current_numbered_sec: dict | None = None
        self._capture_h2: dict | None = None
        self._in_script = False
        self._script_buf: list[str] = []

    def _classes(self, attrs: dict[str, str]) -> set[str]:
        return set((attrs.get("class") or "").split())

    def _has_ancestor(self, pred) -> bool:
        return any(pred(frame) for frame in self.stack)

    def _nearest(self, pred) -> dict | None:
        for frame in reversed(self.stack):
            if pred(frame):
                return frame
        return None

    def handle_starttag(self, tag: str, raw_attrs: list[tuple[str, str | None]]) -> None:
        attrs = {k.lower(): (v if v is not None else "") for k, v in raw_attrs}
        classes = self._classes(attrs)
        frame = {"tag": tag, "attrs": attrs, "classes": classes}

        if tag == "meta":
            name = attrs.get("name", "").lower()
            if name and "content" in attrs:
                self.meta[name] = attrs["content"].strip()
        elif tag == "title":
            self.has_title = True

        el_id = attrs.get("id", "").strip()
        if el_id:
            self.ids[el_id] = self.ids.get(el_id, 0) + 1

        if tag == "main" and "book" in classes:
            self.has_main_book = True

        # Offline & link checks
        if tag in ("script", "img") and attrs.get("src"):
            src = attrs["src"].strip()
            if re.match(r"^https?://", src, re.I):
                self.external_assets.append(f"<{tag} src=\"{src}\">")
            elif not src.startswith("data:"):
                self.local_links.append((tag, src))
        elif tag == "link" and attrs.get("href"):
            href = attrs["href"].strip()
            if re.match(r"^https?://", href, re.I):
                self.external_assets.append(f"<link href=\"{href}\">")
            elif not href.startswith("data:"):
                self.local_links.append((tag, href))
        elif tag == "a" and attrs.get("href"):
            href = attrs["href"].strip()
            if href and not re.match(r"^(?:https?:|mailto:|#|javascript:)", href, re.I):
                self.local_links.append((tag, href))

        # Hardcoded color checks in style="" or SVG attributes
        style = attrs.get("style", "")
        if style and HEX_OR_FUNC_COLOR.search(style):
            self.hardcoded_colors.append(f"<{tag} style=\"{style[:60]}\">")
        in_svg = tag == "svg" or self._has_ancestor(lambda f: f["tag"] == "svg")
        if in_svg:
            for a in SVG_COLOR_ATTRS:
                val = attrs.get(a, "")
                if val and HEX_OR_FUNC_COLOR.search(val):
                    self.hardcoded_colors.append(f"<{tag} {a}=\"{val}\">")

        in_main = self._has_ancestor(lambda f: f["tag"] == "main")
        if in_main:
            if "learn-list" in classes:
                self.has_learn_list = True
            if tag == "nav" and "chapter-nav" in classes:
                self.has_chapter_nav = True

            if tag == "h2":
                if not el_id:
                    self._capture_h2 = {"text": ""}
                if re.match(r"^s\d+$", el_id):
                    sec = {"id": el_id, "has_visual": False}
                    self.sections.append(sec)
                    self.current_numbered_sec = sec
                else:
                    self.current_numbered_sec = None

            if tag == "table" and not self._has_ancestor(lambda f: "table-wrap" in f["classes"]):
                self.tables_unwrapped += 1

            # Visual detection inside numbered sections
            is_visual = (
                "figure" in classes
                or tag == "svg"
                or (tag == "pre" and "diagram" in classes)
            )
            if is_visual and self.current_numbered_sec is not None:
                self.current_numbered_sec["has_visual"] = True

            if "figure" in classes:
                fig = {"has_cap": False}
                self.figures.append(fig)
                frame["figure"] = fig
            if "cap" in classes:
                anc = self._nearest(lambda f: "figure" in f)
                if anc:
                    anc["figure"]["has_cap"] = True

            if "check" in classes:
                chk = {"id": el_id, "correct": 0, "fb_right": False, "fb_wrong": False}
                self.checks.append(chk)
                frame["check"] = chk
            if "data-correct" in attrs:
                anc = self._nearest(lambda f: "check" in f)
                if anc and self._has_ancestor(lambda f: "opts" in f["classes"]):
                    anc["check"]["correct"] += 1
            if "fb" in classes:
                anc = self._nearest(lambda f: "check" in f)
                if anc:
                    if "right" in classes:
                        anc["check"]["fb_right"] = True
                    if "wrong" in classes:
                        anc["check"]["fb_wrong"] = True

        if tag == "script":
            self._in_script = True
            self._script_buf = []

        if tag not in VOID_TAGS:
            self.stack.append(frame)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_script:
            self.scripts.append("".join(self._script_buf))
            self._in_script = False
            self._script_buf = []
        if tag == "h2" and self._capture_h2 is not None:
            self.main_h2_missing_id.append(self._capture_h2["text"].strip() or "(empty)")
            self._capture_h2 = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self._script_buf.append(data)
            return
        if self._capture_h2 is not None:
            self._capture_h2["text"] += data
        if not self._has_ancestor(lambda f: f["tag"] == "main"):
            return
        if self._has_ancestor(lambda f: f["tag"] in ("script", "style", "svg")):
            return
        if not self._has_ancestor(lambda f: f["tag"] in ("pre", "code")):
            self.prose_chunks.append(data)
        if not self._has_ancestor(lambda f: f["tag"] == "details" and "aside" in f["classes"]):
            self.core_words_chunks.append(data)


def load_valid_topics() -> set[str]:
    data = json.loads((ROOT / "curriculum.json").read_text(encoding="utf-8"))
    return {t["id"] for s in data["sections"] for t in s["topics"]}


def lint_file(path: Path, valid_topics: set[str]) -> tuple[list[str], list[str], dict]:
    text = path.read_text(encoding="utf-8")
    p = ChapterParser(path)
    p.feed(text)

    errors: list[str] = []
    warnings: list[str] = []
    is_outline = p.meta.get("status", "").lower() == "outline"

    # 1. Metadata & document shell
    tid = p.meta.get("topic")
    if not tid:
        errors.append('missing <meta name="topic" content="XX.YY">')
    elif tid not in valid_topics:
        errors.append(f'unknown topic id "{tid}" (not in curriculum.json)')
    if not p.has_title:
        errors.append("missing <title>")
    if not p.has_main_book:
        errors.append('missing <main class="content book">')

    # 2. LocalStorage isolation & offline scripts
    all_js = "\n".join(p.scripts)
    if '"gpu-lab:theme"' not in all_js and "'gpu-lab:theme'" not in all_js:
        errors.append('missing inline theme bootstrap using "gpu-lab:theme"')
    for legacy in ("swe-prep:", "model-lab:"):
        if legacy in all_js:
            errors.append(f'legacy localStorage prefix "{legacy}" found in <script>')
    if re.search(r"\bfetch\s*\(", all_js):
        errors.append("fetch() call found in <script> (chapters must work offline over file://)")
    for ext in p.external_assets:
        errors.append(f"external asset violates offline rule: {ext}")

    # 3. Local link existence
    for tag, target in p.local_links:
        clean = target.split("#", 1)[0].split("?", 1)[0]
        if not clean:
            continue
        resolved = (path.parent / clean).resolve()
        if not resolved.exists():
            errors.append(f"broken local link in <{tag}>: {target}")

    # 4. Markup integrity
    for el_id, count in sorted(p.ids.items()):
        if count > 1:
            errors.append(f'duplicate id "{el_id}" ({count}x)')
    for h in p.main_h2_missing_id:
        errors.append(f'h2 without id: "{h}"')
    if p.tables_unwrapped:
        errors.append(f"{p.tables_unwrapped} <table> element(s) not wrapped in .table-wrap")
    for idx, fig in enumerate(p.figures, 1):
        if not fig["has_cap"]:
            errors.append(f".figure #{idx} is missing a .cap caption")
    for idx, chk in enumerate(p.checks, 1):
        name = chk["id"] or f"check #{idx}"
        if not chk["id"].startswith("check-"):
            errors.append(f'{name}: id must start with "check-"')
        if chk["correct"] != 1:
            errors.append(f"{name}: {chk['correct']} options marked data-correct (expected 1)")
        if not (chk["fb_right"] and chk["fb_wrong"]):
            errors.append(f"{name}: must contain both .fb.right and .fb.wrong")

    # 5. Theme-token safety
    for hc in p.hardcoded_colors[:5]:
        errors.append(f"hardcoded color (use CSS var(--token) instead): {hc}")
    if len(p.hardcoded_colors) > 5:
        errors.append(f"...and {len(p.hardcoded_colors) - 5} more hardcoded colors")

    # 6. Raw Markdown & unescaped special tokens in HTML
    prose = "\n".join(p.prose_chunks)
    for m in RAW_BACKTICKS.findall(prose)[:5]:
        errors.append(f"raw Markdown backticks in HTML prose (use <code>): {m}")
    for m in RAW_MD_BOLD.findall(prose)[:5]:
        errors.append(f"raw Markdown bold in HTML prose (use <b>): {m}")
    html_no_scripts = re.sub(r"<script\b[^>]*>.*?</script>", "", text, flags=re.I | re.S)
    html_no_comments = re.sub(r"<!--.*?-->", "", html_no_scripts, flags=re.S)
    for m in UNESCAPED_TURN.findall(html_no_comments)[:3]:
        errors.append(f"unescaped special token in HTML (escape with &lt; / &gt;): {m}")

    # 7. First-principles pacing & anti-slop (complete chapters only)
    words = len(" ".join(p.core_words_chunks).split())
    if not is_outline:
        if not p.has_learn_list:
            errors.append("missing .learn-list block")
        if "summary" not in p.ids:
            errors.append('missing <h2 id="summary">')
        if "review" not in p.ids:
            errors.append('missing <div class="review" id="review">')
        if not p.has_chapter_nav:
            errors.append("missing <nav class=\"chapter-nav\">")

        # Early visual rule (s1 or s2)
        early = [s for s in p.sections if s["id"] in ("s1", "s2")]
        if early and not any(s["has_visual"] for s in early):
            errors.append("missing early visual (.figure, <svg>, or pre.diagram) in Section 1 or 2")

        # Max 2 consecutive numbered sections without a visual
        dry_run: list[str] = []
        for s in p.sections:
            if s["has_visual"]:
                dry_run = []
            else:
                dry_run.append(s["id"])
                if len(dry_run) > 2:
                    errors.append(
                        f"visual desert: {len(dry_run)} consecutive sections without a visual ({', '.join(dry_run)})"
                    )
                    break

        if not (5 <= len(p.checks) <= 8):
            warnings.append(f"quick checks: {len(p.checks)} (target 5–8)")
        if not (1800 <= words <= 3600):
            warnings.append(f"visible core-path word count: {words} (target ~2,000–3,500)")

        slop_hits = sorted({m.lower() for m in ANTI_SLOP.findall(prose)})
        if slop_hits:
            warnings.append(f"banned filler prose detected: {', '.join(slop_hits)}")

    stats = {
        "outline": is_outline,
        "words": words,
        "checks": len(p.checks),
        "sections": len(p.sections),
        "visual_sections": sum(1 for s in p.sections if s["has_visual"]),
    }
    return errors, warnings, stats


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="*", type=Path, help="HTML chapter file(s) to check")
    ap.add_argument("--all", action="store_true", help="check all completed chapters in book/sections/*/concepts/")
    ap.add_argument("--include-outlines", action="store_true", help="with --all, also lint outline pages")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args(argv)

    targets = list(args.pages)
    if args.all:
        for f in sorted(ROOT.glob("book/sections/*/concepts/*.html")):
            if not args.include_outlines and 'name="status" content="outline"' in f.read_text(encoding="utf-8"):
                continue
            targets.append(f)

    if not targets:
        ap.error("provide at least one HTML page or pass --all")

    valid_topics = load_valid_topics()
    failed = 0
    for page in targets:
        if not page.is_file():
            print(f"✗ {page}: file not found")
            failed += 1
            continue
        errors, warnings, stats = lint_file(page, valid_topics)
        rel = page.resolve().relative_to(ROOT) if page.resolve().is_relative_to(ROOT) else page
        tag = "outline" if stats["outline"] else f"{stats['words']}w · {stats['checks']} checks · {stats['visual_sections']}/{stats['sections']} visual secs"
        if errors or (args.strict and warnings):
            failed += 1
            print(f"✗ {rel} ({tag})")
        elif warnings:
            print(f"! {rel} ({tag})")
        else:
            print(f"✓ {rel} ({tag})")
        for e in errors:
            print(f"    ERROR: {e}")
        for w in warnings:
            print(f"    WARN:  {w}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
