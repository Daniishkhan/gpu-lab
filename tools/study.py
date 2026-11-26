#!/usr/bin/env python3
"""
Local Study Cockpit server for gpu/lab (zero external dependencies).

Designed for Antigravity IDE's embedded Simple Browser alongside your local CPU
exercises (`exercises/`) and loop-tracing debugger (`.vscode/launch.json`):

  - Serves the offline HTML book (`book/`) at `/` while keeping static HTML
    files 100% offline-compatible for `file://` and GitHub Pages.
  - Renders Markdown files (`gpu-labs/**/README.md`, `journal/**/*.md`,
    `README.md`, `GEMINI.md`) on the fly in the exact gpu/lab book theme.
  - Injects a lightweight local cockpit layer over `127.0.0.1`:
      * Scroll-preserving live reload when you or Antigravity edit a chapter.
      * Auto-runs `pytest --tb=short -l` on save for the edited exercise and
        streams per-test pass/fail + AST line numbers + local-var tracebacks
        over Server-Sent Events (`/api/events`).
      * 1-click "Open .py" / "Open tests" / "Debug :L<line>" via Antigravity
        IDE CLI (`--reuse-window --goto`).
      * 1-click "Copy trace prompt" on every failing test for loop-by-loop
        Socratic debugging in Antigravity chat (`trace-and-debug` skill).
      * Sticky "Last saved exercise" bar that keeps live test status visible
        even when you jump to `python-cheatsheet.html` or another chapter.

Usage:
  python3 tools/study.py                  # serve at http://127.0.0.1:8000
  python3 tools/study.py --port 8010      # custom port
  python3 tools/study.py --no-watch       # disable file watcher
"""
from __future__ import annotations

import argparse
import ast
import html as html_mod
import importlib.util
import json
import mimetypes
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import xml.etree.ElementTree as ET
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK_ROOT = ROOT / "book"
EX_ROOT = ROOT / "exercises"
LABS_ROOT = ROOT / "gpu-labs"
JOURNAL_ROOT = ROOT / "journal"
RESULTS_PATH = ROOT / ".test-results.json"

ANTIGRAVITY_IDE_CLI = "/Applications/Antigravity IDE.app/Contents/Resources/app/bin/antigravity-ide"

EX_TOPIC_RE = re.compile(r"^Topic:\s*([\d.]+)(.*)$", re.M)
TOPIC_ID_RE = re.compile(r"\b\d{2}\.\d{2}\b")
IGNORED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "_site", "node_modules", "scratch"}


# ---------------------------------------------------------------------------
# Python / Editor discovery
# ---------------------------------------------------------------------------

def resolve_python() -> str:
    venv_py = ROOT / ".venv" / "bin" / "python"
    if venv_py.is_file():
        return str(venv_py)
    return sys.executable


def resolve_editor_cmd() -> list[str] | None:
    env_ed = os.environ.get("GPU_LAB_EDITOR", "").strip()
    if env_ed:
        return [env_ed]
    if Path(ANTIGRAVITY_IDE_CLI).is_file():
        return [ANTIGRAVITY_IDE_CLI]
    for name in ("antigravity-ide", "code", "cursor"):
        found = shutil.which(name)
        if found:
            return [found]
    return None


def open_in_ide(abs_path: Path, line: int | None = None) -> tuple[bool, str]:
    target = f"{abs_path}:{line}" if line and line > 0 else str(abs_path)
    editor = resolve_editor_cmd()
    try:
        if editor:
            cmd = [*editor, "--reuse-window", "--goto", target]
            subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=ROOT,
            )
            return True, f"Opened {abs_path.relative_to(ROOT)}" + (f":{line}" if line else "")
        if sys.platform == "darwin":
            subprocess.Popen(
                ["open", str(abs_path)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True, f"Opened {abs_path.relative_to(ROOT)}"
    except OSError as exc:
        return False, f"Failed to open editor: {exc}"
    return False, "No IDE CLI found (set GPU_LAB_EDITOR or install antigravity-ide/code on PATH)"


def safe_path_under(base: Path, rel_str: str) -> Path | None:
    clean = urllib.parse.unquote(rel_str).lstrip("/")
    if not clean or "\x00" in clean:
        return None
    try:
        candidate = (base / clean).resolve()
        candidate.relative_to(base.resolve())
    except (OSError, ValueError):
        return None
    return candidate


def safe_repo_path(rel_str: str) -> Path | None:
    return safe_path_under(ROOT, rel_str)


# ---------------------------------------------------------------------------
# Exercise & Lab index + AST line-number lookup
# ---------------------------------------------------------------------------

def extract_test_lines(test_path: Path) -> dict[str, int]:
    lines: dict[str, int] = {}
    if not test_path.is_file():
        return lines
    try:
        tree = ast.parse(test_path.read_text(encoding="utf-8"), filename=str(test_path))
    except SyntaxError:
        return lines
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            lines[node.name] = node.lineno
    return lines


def scan_exercises() -> dict[str, dict]:
    """Return {module_name: metadata} for every CPU exercise under exercises/."""
    exercises: dict[str, dict] = {}
    if not EX_ROOT.is_dir():
        return exercises
    for sec_dir in sorted(EX_ROOT.iterdir()):
        if not sec_dir.is_dir() or sec_dir.name in IGNORED_DIRS:
            continue
        sec_id = sec_dir.name.split("-", 1)[0]
        for stub in sorted(sec_dir.glob("*.py")):
            if stub.name.startswith(("test_", "_")) or stub.name == "conftest.py":
                continue
            mod = stub.stem
            test_file = sec_dir / f"test_{mod}.py"
            try:
                text = stub.read_text(encoding="utf-8")
            except OSError:
                text = ""
            m = EX_TOPIC_RE.search(text)
            topics = [m.group(1)] + TOPIC_ID_RE.findall(m.group(2)) if m else []
            doc_title = (
                text.split('"""')[1].strip().splitlines()[0]
                if text.startswith('"""') and '"""' in text[3:]
                else mod
            )
            exercises[mod] = {
                "module": mod,
                "section": sec_id,
                "slug": sec_dir.name,
                "title": doc_title,
                "topics": topics,
                "stub_path": stub.relative_to(ROOT).as_posix(),
                "test_path": test_file.relative_to(ROOT).as_posix() if test_file.is_file() else None,
                "test_lines": extract_test_lines(test_file),
            }
    return exercises


def _md_title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return path.parent.name if path.name == "README.md" else path.stem


def scan_labs() -> list[dict]:
    if not LABS_ROOT.is_dir():
        return []
    out: list[dict] = []
    readme = LABS_ROOT / "README.md"
    if readme.is_file():
        out.append({"label": "Overview", "path": "gpu-labs/README.md", "title": _md_title(readme)})
    for item in sorted(LABS_ROOT.iterdir()):
        if item.is_dir() and (item / "README.md").is_file():
            f = item / "README.md"
            out.append({"label": item.name, "path": f.relative_to(ROOT).as_posix(), "title": _md_title(f)})
        elif item.is_file() and item.suffix == ".md" and item.name != "README.md":
            out.append({"label": item.stem, "path": item.relative_to(ROOT).as_posix(), "title": _md_title(item)})
    return out


# ---------------------------------------------------------------------------
# SSE Hub & Test Runner State
# ---------------------------------------------------------------------------

class EventHub:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._clients: set[queue.Queue[tuple[str, dict]]] = set()

    def subscribe(self) -> queue.Queue[tuple[str, dict]]:
        q: queue.Queue[tuple[str, dict]] = queue.Queue(maxsize=64)
        with self._lock:
            self._clients.add(q)
        return q

    def unsubscribe(self, q: queue.Queue[tuple[str, dict]]) -> None:
        with self._lock:
            self._clients.discard(q)

    def broadcast(self, event: str, data: dict) -> None:
        with self._lock:
            clients = list(self._clients)
        for q in clients:
            try:
                q.put_nowait((event, data))
            except queue.Full:
                pass


class CockpitState:
    def __init__(self) -> None:
        self.hub = EventHub()
        self._lock = threading.Lock()
        self._run_locks: dict[str, threading.Lock] = {}
        self.exercises: dict[str, dict] = scan_exercises()
        self.labs: list[dict] = scan_labs()
        self.results: dict[str, dict] = {}
        self.last_module: str | None = None
        self._load_cached_results()

    def _load_cached_results(self) -> None:
        if not RESULTS_PATH.is_file():
            return
        try:
            raw = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        for mod, summary in raw.items():
            if isinstance(summary, dict) and "passed" in summary and "total" in summary:
                self.results[mod] = {
                    "module": mod,
                    "passed": int(summary["passed"]),
                    "total": int(summary["total"]),
                    "failed": max(0, int(summary["total"]) - int(summary["passed"])),
                    "cases": [],
                    "error": None,
                    "updated_at": None,
                }

    def refresh_index(self) -> None:
        exs = scan_exercises()
        labs = scan_labs()
        with self._lock:
            self.exercises = exs
            self.labs = labs

    def _persist_summary(self) -> None:
        with self._lock:
            summary = {
                mod: {"passed": r["passed"], "total": r["total"]}
                for mod, r in self.results.items()
                if r.get("total", 0) > 0
            }
        try:
            RESULTS_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "editor_available": resolve_editor_cmd() is not None,
                "exercises": self.exercises,
                "results": self.results,
                "labs": self.labs,
                "last_module": self.last_module,
            }

    def _module_lock(self, mod: str) -> threading.Lock:
        with self._lock:
            if mod not in self._run_locks:
                self._run_locks[mod] = threading.Lock()
            return self._run_locks[mod]

    def run_module_tests(self, mod: str) -> dict:
        self.refresh_index()
        with self._lock:
            meta = self.exercises.get(mod)
        if not meta or not meta.get("test_path"):
            return {"module": mod, "error": f"Unknown exercise module: {mod}", "passed": 0, "total": 0, "failed": 0, "cases": []}

        lock = self._module_lock(mod)
        with lock:
            with self._lock:
                self.last_module = mod
            self.hub.broadcast("test-running", {"module": mod})
            test_abs = ROOT / meta["test_path"]
            test_lines = extract_test_lines(test_abs)
            with self._lock:
                if mod in self.exercises:
                    self.exercises[mod]["test_lines"] = test_lines

            py = resolve_python()
            if importlib.util.find_spec("pytest") is None and not (ROOT / ".venv" / "bin" / "pytest").is_file():
                pytest_bin = shutil.which("pytest")
                cmd_base = [pytest_bin] if pytest_bin else [py, "-m", "pytest"]
            else:
                cmd_base = [py, "-m", "pytest"]

            fd, xml_str = tempfile.mkstemp(prefix=f"gpu_lab_{mod}_", suffix=".xml")
            os.close(fd)
            xml_path = Path(xml_str)
            try:
                proc = subprocess.run(
                    cmd_base + [
                        str(test_abs),
                        "-q",
                        "--no-header",
                        "--tb=short",
                        "-l",
                        "-p", "no:cacheprovider",
                        f"--junitxml={xml_path}",
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=90,
                )
                result = self._parse_junit(mod, xml_path, test_lines, proc)
            except subprocess.TimeoutExpired:
                result = {
                    "module": mod,
                    "passed": 0,
                    "total": len(test_lines),
                    "failed": len(test_lines),
                    "cases": [],
                    "error": "pytest timed out after 90s (check for an infinite loop!)",
                    "updated_at": time.time(),
                }
            finally:
                try:
                    xml_path.unlink(missing_ok=True)
                except OSError:
                    pass

            with self._lock:
                self.results[mod] = result
                self.last_module = mod
            self._persist_summary()
            self.hub.broadcast("test-result", result)
            return result

    def _parse_junit(
        self,
        mod: str,
        xml_path: Path,
        test_lines: dict[str, int],
        proc: subprocess.CompletedProcess[str],
    ) -> dict:
        cases: list[dict] = []
        passed = 0
        failed = 0
        collection_error: str | None = None

        if xml_path.is_file() and xml_path.stat().st_size > 0:
            try:
                root = ET.parse(xml_path).getroot()
                for tc in root.iter("testcase"):
                    raw_name = tc.get("name", "") or "collection"
                    base_name = raw_name.split("[", 1)[0]
                    line = test_lines.get(base_name)
                    failure = tc.find("failure")
                    error = tc.find("error")
                    skipped = tc.find("skipped")
                    if failure is not None or error is not None:
                        node = failure if failure is not None else error
                        status = "error" if error is not None else "failed"
                        msg = (node.get("message") or "").strip().splitlines()[0] if node.get("message") else ""
                        body = (node.text or "").strip()
                        tail_lines = body.splitlines()[-16:] if body else []
                        if not msg and tail_lines:
                            msg = tail_lines[-1]
                        if not raw_name or raw_name == "collection" or "collection failure" in msg.lower():
                            collection_error = "\n".join(tail_lines) or msg
                        else:
                            failed += 1
                            cases.append({
                                "name": raw_name,
                                "status": status,
                                "line": line,
                                "message": msg[:260],
                                "detail": "\n".join(tail_lines),
                            })
                    elif skipped is not None:
                        cases.append({
                            "name": raw_name,
                            "status": "skipped",
                            "line": line,
                            "message": (skipped.get("message") or "skipped")[:200],
                            "detail": "",
                        })
                    else:
                        passed += 1
                        cases.append({
                            "name": raw_name,
                            "status": "passed",
                            "line": line,
                            "message": "",
                            "detail": "",
                        })
            except ET.ParseError:
                pass

        if not cases and proc.returncode != 0 and not collection_error:
            combined = (proc.stdout + "\n" + proc.stderr).strip()
            collection_error = "\n".join(combined.splitlines()[-16:]) or f"pytest exited with code {proc.returncode}"

        total = len(cases)
        return {
            "module": mod,
            "passed": passed,
            "failed": failed,
            "total": total,
            "cases": cases,
            "error": collection_error,
            "updated_at": time.time(),
        }

    def run_all_tests_async(self) -> None:
        def _worker() -> None:
            self.refresh_index()
            with self._lock:
                mods = sorted(self.exercises.keys())
            for mod in mods:
                self.run_module_tests(mod)
        threading.Thread(target=_worker, daemon=True).start()


# ---------------------------------------------------------------------------
# Pure-stdlib Markdown → gpu/lab Book HTML renderer
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    plain = re.sub(r"`([^`]+)`", r"\1", text)
    plain = re.sub(r"[^a-zA-Z0-9\s-]", "", plain).strip().lower()
    return re.sub(r"[\s-]+", "-", plain) or "section"


def _book_web_href(rel_posix: str) -> str:
    """Convert repo-relative path to web path served by Study Cockpit."""
    if rel_posix.startswith("book/"):
        return "/" + rel_posix[5:]
    return "/" + rel_posix


def _render_inline(text: str, rel_dir: Path, known_exercises: dict[str, dict]) -> str:
    """Render inline Markdown (code spans, links, bold, italic) safely."""
    tokens: list[str] = []

    def stash(html_frag: str) -> str:
        idx = len(tokens)
        tokens.append(html_frag)
        return f"\x00TOK{idx}\x00"

    # 1. Links: [label](url)
    def repl_link(m: re.Match[str]) -> str:
        raw_label, raw_href = m.group(1), m.group(2).strip()
        label_html = _render_inline(raw_label, rel_dir, known_exercises)
        attrs = ""
        href = raw_href
        if re.match(r"^https?://", href, re.I):
            attrs = ' target="_blank" rel="noopener"'
        elif href.endswith(".py"):
            resolved = (rel_dir / href).as_posix()
            safe = safe_repo_path(resolved)
            if safe:
                rel_posix = safe.relative_to(ROOT).as_posix()
                attrs = f' data-ide-open="{html_mod.escape(rel_posix, quote=True)}"'
        return stash(f'<a href="{html_mod.escape(href, quote=True)}"{attrs}>{label_html}</a>')

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", repl_link, text)

    # 2. Inline code: `...`
    def repl_code(m: re.Match[str]) -> str:
        code = m.group(1)
        esc = html_mod.escape(code)
        if code.endswith(".py") and "/" not in code and code[:-3] in known_exercises:
            stub = known_exercises[code[:-3]]["stub_path"]
            return stash(
                f'<a href="/{html_mod.escape(stub, quote=True)}" '
                f'data-ide-open="{html_mod.escape(stub, quote=True)}" '
                f'title="Open {esc} in IDE"><code>{esc}</code></a>'
            )
        if ("/" in code or code.endswith((".html", ".md"))) and not code.startswith(("http", "~", "$")):
            cand = safe_repo_path(code) or safe_path_under(BOOK_ROOT, code)
            if cand and cand.is_file():
                rel_posix = cand.relative_to(ROOT).as_posix()
                if code.endswith(".py"):
                    return stash(
                        f'<a href="/{html_mod.escape(rel_posix, quote=True)}" '
                        f'data-ide-open="{html_mod.escape(rel_posix, quote=True)}"><code>{esc}</code></a>'
                    )
                if code.endswith((".html", ".md")):
                    web = _book_web_href(rel_posix)
                    return stash(f'<a href="{html_mod.escape(web, quote=True)}"><code>{esc}</code></a>')
        return stash(f"<code>{esc}</code>")

    text = re.sub(r"`([^`\n]+)`", repl_code, text)

    # 3. Escape remaining HTML
    text = html_mod.escape(text)

    # 4. Bold & italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)

    # 5. Restore stashed fragments
    for idx, frag in enumerate(tokens):
        text = text.replace(f"\x00TOK{idx}\x00", frag)
    return text


def render_markdown_body(md_text: str, rel_path: Path, known_exercises: dict[str, dict]) -> tuple[str, str]:
    """Convert Markdown text to (page_title, main_html_body) using gpu/lab classes."""
    lines = md_text.splitlines()
    rel_dir = rel_path.parent
    out: list[str] = []
    title = rel_path.name
    seen_h1 = False
    used_ids: set[str] = set()
    check_idx = 0
    i = 0
    n = len(lines)

    def unique_id(base: str) -> str:
        slug = _slugify(base)
        cand = slug
        k = 2
        while cand in used_ids:
            cand = f"{slug}-{k}"
            k += 1
        used_ids.add(cand)
        return cand

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Fenced code block
        fence_m = re.match(r"^```([A-Za-z0-9_+-]*)\s*$", stripped)
        if fence_m:
            lang = fence_m.group(1).lower()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            code_text = "\n".join(buf)
            pre_cls = "" if lang in ("python", "py") else ' class="plain"'
            out.append(
                f'<div class="study-code-wrap">'
                f'<pre{pre_cls}><code>{html_mod.escape(code_text)}</code></pre>'
                f'<button class="copy-btn study-code-copy" type="button">Copy</button>'
                f'</div>'
            )
            continue

        # Horizontal rule
        if re.match(r"^(?:-{3,}|\*{3,}|_{3,})$", stripped):
            out.append("<hr>")
            i += 1
            continue

        # Headings
        hm = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if hm:
            lvl = len(hm.group(1))
            raw_heading = hm.group(2).strip()
            if lvl == 1 and not seen_h1:
                seen_h1 = True
                title = re.sub(r"`([^`]+)`", r"\1", raw_heading)
                top = rel_path.parts[0] if rel_path.parts else ""
                eyebrow = (
                    "Cloud GPU Lab Runbook" if top == "gpu-labs"
                    else "Study Journal" if top == "journal"
                    else "Repository Guide"
                )
                out.append(
                    f'<header class="chapter-head">'
                    f'<div class="eyebrow">{eyebrow} · <code>{html_mod.escape(rel_path.as_posix())}</code></div>'
                    f'<h1>{_render_inline(raw_heading, rel_dir, known_exercises)}</h1>'
                    f'</header>'
                )
            elif lvl == 2:
                hid = unique_id(raw_heading)
                num_m = re.match(r"^(\d+)\.\s+(.*)$", raw_heading)
                if num_m:
                    num, rest = num_m.group(1), num_m.group(2)
                    out.append(
                        f'<h2 id="{hid}"><span class="sec-num">{num}</span>'
                        f'{_render_inline(rest, rel_dir, known_exercises)}</h2>'
                    )
                else:
                    out.append(f'<h2 id="{hid}">{_render_inline(raw_heading, rel_dir, known_exercises)}</h2>')
            else:
                out.append(f"<h{lvl}>{_render_inline(raw_heading, rel_dir, known_exercises)}</h{lvl}>")
            i += 1
            continue

        # Blockquote -> .callout
        if stripped.startswith(">"):
            q_lines = []
            while i < n and lines[i].strip().startswith(">"):
                q_lines.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            out.append(f'<div class="callout">{_render_inline(" ".join(q_lines), rel_dir, known_exercises)}</div>')
            continue

        # GFM Table
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)+\|?\s*$", lines[i + 1]):
            def split_row(r: str) -> list[str]:
                r = r.strip()
                if r.startswith("|"):
                    r = r[1:]
                if r.endswith("|"):
                    r = r[:-1]
                return [c.strip() for c in r.split("|")]

            headers = split_row(line)
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1
            th_html = "".join(f"<th>{_render_inline(c, rel_dir, known_exercises)}</th>" for c in headers)
            tr_html = "".join(
                "<tr>" + "".join(f"<td>{_render_inline(c, rel_dir, known_exercises)}</td>" for c in r) + "</tr>"
                for r in rows
            )
            out.append(f'<div class="table-wrap"><table><thead><tr>{th_html}</tr></thead><tbody>{tr_html}</tbody></table></div>')
            continue

        # Unordered / Task list
        if re.match(r"^[-*]\s+", stripped):
            items = []
            is_checklist = False
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                item_text = re.sub(r"^\s*[-*]\s+", "", lines[i]).strip()
                cb_m = re.match(r"^\[([ xX])\]\s+(.*)$", item_text)
                if cb_m:
                    is_checklist = True
                    checked = " checked" if cb_m.group(1).lower() == "x" else ""
                    key = f"{rel_path.as_posix()}:{check_idx}"
                    check_idx += 1
                    body_html = _render_inline(cb_m.group(2), rel_dir, known_exercises)
                    items.append(
                        f'<li><label class="check-row">'
                        f'<input type="checkbox" data-md-check="{html_mod.escape(key, quote=True)}"{checked}>'
                        f'<span>{body_html}</span></label></li>'
                    )
                else:
                    items.append(f"<li>{_render_inline(item_text, rel_dir, known_exercises)}</li>")
                i += 1
            cls = ' class="study-checklist"' if is_checklist else ""
            out.append(f"<ul{cls}>{''.join(items)}</ul>")
            continue

        # Ordered list
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                item_text = re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip()
                items.append(f"<li>{_render_inline(item_text, rel_dir, known_exercises)}</li>")
                i += 1
            out.append(f"<ol>{''.join(items)}</ol>")
            continue

        # Paragraph
        p_lines = []
        while i < n:
            cur = lines[i].strip()
            if (
                not cur
                or cur.startswith(("#", "```", ">"))
                or re.match(r"^(?:[-*]\s+|\d+\.\s+|-{3,}|\*{3,})$", cur)
            ):
                break
            p_lines.append(cur)
            i += 1
        out.append(f"<p>{_render_inline(' '.join(p_lines), rel_dir, known_exercises)}</p>")

    return title, "\n".join(out)


def render_markdown_page(md_path: Path, state: CockpitState) -> bytes:
    rel = md_path.relative_to(ROOT)
    md_text = md_path.read_text(encoding="utf-8")
    title, body_html = render_markdown_body(md_text, rel, state.exercises)

    nav_html = ""
    if rel.parts and rel.parts[0] == "gpu-labs":
        lab_links = []
        for lb in state.labs:
            active = ' class="study-lab-pill active"' if lb["path"] == rel.as_posix() else ' class="study-lab-pill"'
            lab_links.append(f'<a{active} href="/{html_mod.escape(lb["path"], quote=True)}">{html_mod.escape(lb["label"])}</a>')
        nav_html = f'<div class="study-lab-bar"><span class="muted small">GPU Labs:</span> {" ".join(lab_links)}</div>'

    # Absolute root-relative assets work cleanly at any depth on localhost
    doc = f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html_mod.escape(title)} · gpu/lab</title>
  <script>try {{ document.documentElement.dataset.theme = JSON.parse(localStorage.getItem("gpu-lab:theme")) || "dark"; }} catch (e) {{}}</script>
  <link rel="stylesheet" href="/assets/style.css">
  <script src="/assets/curriculum.js"></script>
  <script src="/assets/shell.js"></script>
  <script src="/assets/book.js"></script>
</head>
<body data-root="" data-page="lab" data-source-file="{html_mod.escape(rel.as_posix(), quote=True)}">
<main class="content book">
{nav_html}
{body_html}
</main>
</body>
</html>
"""
    return inject_cockpit(doc.encode("utf-8"), source_rel=rel.as_posix())


# ---------------------------------------------------------------------------
# Cockpit CSS & JS (served dynamically from /__study/* — 100% theme-token based)
# ---------------------------------------------------------------------------

COCKPIT_CSS = """
/* gpu/lab Local Study Cockpit — uses only book/assets/style.css theme tokens */
.study-pill {
  display: inline-flex; align-items: center; gap: 6px;
  font: 600 0.72rem/1 var(--mono); padding: 5px 9px; border-radius: 999px;
  border: 1px solid var(--border-strong); background: var(--surface); color: var(--muted);
  white-space: nowrap;
}
.study-dot {
  width: 7px; height: 7px; border-radius: 50%; background: var(--ok);
  display: inline-block; flex: none;
}
.study-pill.running .study-dot { background: var(--warn); animation: study-pulse 0.9s infinite alternate; }
.study-pill.offline .study-dot { background: var(--bad); }
@keyframes study-pulse { from { opacity: 0.35; } to { opacity: 1; } }

.study-ide-btn {
  display: inline-flex; align-items: center; gap: 5px; cursor: pointer;
  font: 600 0.75rem/1 var(--ui); padding: 6px 10px; border-radius: 7px;
  border: 1px solid var(--border-strong); background: var(--surface); color: var(--text);
  transition: border-color 0.12s, background 0.12s, color 0.12s;
  white-space: nowrap; text-decoration: none;
}
.study-ide-btn:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); text-decoration: none; }
.study-ide-btn.primary { border-color: var(--accent); background: var(--accent-soft); color: var(--accent); }
.study-ide-btn.trace { border-color: color-mix(in srgb, var(--accent-2) 45%, var(--border-strong)); color: var(--accent-2); }
.study-ide-btn.trace:hover { border-color: var(--accent-2); background: color-mix(in srgb, var(--accent-2) 14%, transparent); color: var(--accent-2); }
.study-ide-btn.copied { border-color: var(--ok); color: var(--ok); background: var(--ok-soft); }
.study-ide-btn.sm { padding: 4px 8px; font-size: 0.72rem; }

.study-dock {
  margin: 0 0 26px; border: 1px solid var(--border-strong); border-radius: var(--radius-lg);
  background: var(--surface); overflow: hidden; font-family: var(--ui);
}
.study-dock-head {
  display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap;
  padding: 10px 14px; background: var(--surface-2); border-bottom: 1px solid var(--border);
}
.study-dock-title {
  font: 700 0.72rem/1 var(--mono); text-transform: uppercase; letter-spacing: 0.08em; color: var(--brand);
  display: inline-flex; align-items: center; gap: 7px;
}
.study-dock-tip { font-size: 0.78rem; color: var(--muted); }
.study-dock-tip kbd { font-size: 0.7rem; }

.study-ex-row {
  padding: 12px 14px; border-top: 1px solid var(--border);
  display: flex; flex-direction: column; gap: 8px;
}
.study-ex-row:first-of-type { border-top: 0; }
.study-ex-main { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.study-ex-mod { font: 650 0.88rem var(--mono); color: var(--text-strong); }
.study-ex-actions { display: inline-flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-left: auto; }

.study-badge {
  display: inline-flex; align-items: center; gap: 4px;
  font: 600 0.72rem/1 var(--mono); padding: 4px 8px; border-radius: 6px;
  border: 1px solid var(--border); background: var(--bg-2); color: var(--muted);
}
.study-badge.pass { color: var(--ok); background: var(--ok-soft); border-color: color-mix(in srgb, var(--ok) 40%, transparent); }
.study-badge.fail { color: var(--bad); background: var(--bad-soft); border-color: color-mix(in srgb, var(--bad) 40%, transparent); }
.study-badge.run { color: var(--warn); background: var(--warn-soft); border-color: color-mix(in srgb, var(--warn) 40%, transparent); }

.study-cases {
  margin: 2px 0 0; padding: 8px 10px; border-radius: 8px;
  background: var(--bg-2); border: 1px solid var(--border);
  display: flex; flex-direction: column; gap: 6px;
}
.study-cases[hidden] { display: none; }
.study-case {
  display: grid; grid-template-columns: auto minmax(0, 1fr) auto; gap: 4px 10px;
  align-items: baseline; font-size: 0.82rem; padding: 4px 0;
  border-top: 1px solid var(--border);
}
.study-case:first-child { border-top: 0; padding-top: 0; }
.study-case-mark { font: 700 0.82rem var(--mono); }
.study-case.passed .study-case-mark { color: var(--ok); }
.study-case.failed .study-case-mark, .study-case.error .study-case-mark { color: var(--bad); }
.study-case.skipped .study-case-mark { color: var(--warn); }
.study-case-name { font: 550 0.8rem var(--mono); color: var(--text-strong); word-break: break-word; }
.study-case-btns { display: inline-flex; gap: 5px; flex-wrap: wrap; justify-content: flex-end; }
.study-case-msg {
  grid-column: 2 / -1; font: 0.76rem/1.45 var(--mono); color: var(--bad);
  background: var(--bad-soft); padding: 5px 8px; border-radius: 6px; white-space: pre-wrap; word-break: break-word;
}
.study-case-trace { grid-column: 2 / -1; margin-top: 2px; font-size: 0.76rem; }
.study-case-trace > summary { cursor: pointer; color: var(--muted); font: 550 0.74rem var(--ui); user-select: none; }
.study-case-trace > summary:hover { color: var(--accent); }
.study-case-trace > pre {
  margin: 5px 0 0; padding: 8px 10px; border-radius: 6px;
  background: var(--surface); border: 1px solid var(--border);
  font: 0.74rem/1.45 var(--mono); color: var(--text); overflow-x: auto; white-space: pre-wrap;
}
.study-err-box {
  font: 0.76rem/1.45 var(--mono); color: var(--bad); background: var(--bad-soft);
  border: 1px solid color-mix(in srgb, var(--bad) 35%, transparent);
  padding: 8px 10px; border-radius: 8px; white-space: pre-wrap; overflow-x: auto; margin: 0;
}

/* Sticky Last-Saved Exercise Bar (stays visible across cheatsheets & chapters) */
body.has-study-bar { padding-bottom: 64px; }
.study-sticky {
  position: fixed; left: 12px; right: 12px; bottom: 10px; z-index: 160;
  max-width: 960px; margin: 0 auto;
  border: 1px solid var(--border-strong); border-radius: 11px;
  background: var(--surface-2); box-shadow: var(--shadow);
  font-family: var(--ui); overflow: hidden;
}
.study-sticky-row {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 8px 12px;
}
.study-sticky-tag { font: 700 0.68rem/1 var(--mono); text-transform: uppercase; letter-spacing: 0.08em; color: var(--brand); }
.study-sticky-drawer {
  max-height: 44vh; overflow-y: auto; padding: 10px 12px;
  border-bottom: 1px solid var(--border); background: var(--bg-2);
}
.study-sticky-drawer[hidden] { display: none; }

.study-lab-bar {
  display: flex; flex-wrap: wrap; align-items: center; gap: 6px;
  margin-bottom: 18px; padding-bottom: 12px; border-bottom: 1px solid var(--border);
  font-family: var(--ui);
}
.study-lab-pill {
  font: 550 0.76rem/1 var(--mono); padding: 5px 9px; border-radius: 6px;
  border: 1px solid var(--border); background: var(--surface); color: var(--muted);
}
.study-lab-pill:hover { border-color: var(--accent); color: var(--accent); text-decoration: none; }
.study-lab-pill.active { border-color: var(--accent); background: var(--accent-soft); color: var(--accent); }

.study-checklist { list-style: none; padding-left: 0; }
.study-checklist li { margin: 8px 0; }

.study-code-wrap { position: relative; }
.study-code-copy { position: absolute; top: 8px; right: 8px; z-index: 2; }

.study-toast {
  position: fixed; bottom: 66px; right: 18px; z-index: 200;
  padding: 9px 14px; border-radius: 9px;
  background: var(--surface-2); border: 1px solid var(--border-strong); color: var(--text-strong);
  font: 550 0.8rem/1.3 var(--ui); box-shadow: var(--shadow);
  opacity: 0; transform: translateY(6px); pointer-events: none;
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.study-toast.show { opacity: 1; transform: translateY(0); }

.study-tbl-actions { display: inline-flex; gap: 5px; flex-wrap: wrap; align-items: center; }
"""

COCKPIT_JS = r"""
/* gpu/lab Local Study Cockpit — injected only by tools/study.py over localhost */
(function () {
  if (window.__GPU_LAB_COCKPIT__) return;
  window.__GPU_LAB_COCKPIT__ = true;

  const SCROLL_KEY = "gpu-lab:study-scroll:" + location.pathname;
  const store = window.SWEStore || {
    get(k, d) { try { const v = localStorage.getItem("gpu-lab:" + k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem("gpu-lab:" + k, JSON.stringify(v)); } catch (_) {} },
  };

  let state = { exercises: {}, results: {}, labs: [], last_module: null, editor_available: true };
  let toastEl = null;
  let toastTimer = null;
  let statusPill = null;
  let stickyDismissed = false;
  let stickyDrawerOpen = false;
  const openDetails = new Set();

  function toast(msg, ms = 2200) {
    if (!toastEl) {
      toastEl = document.createElement("div");
      toastEl.className = "study-toast";
      document.body.append(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("show"), ms);
  }

  function copyText(text, btn, doneLabel = "Copied ✓") {
    const finish = () => {
      if (btn) {
        const orig = btn.textContent;
        btn.textContent = doneLabel;
        btn.classList.add("copied");
        setTimeout(() => { btn.textContent = orig; btn.classList.remove("copied"); }, 1400);
      } else {
        toast(doneLabel);
      }
    };
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(text).then(finish, fallback);
    } else fallback();
    function fallback() {
      const ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.append(ta); ta.select();
      try { document.execCommand("copy"); } catch (_) {}
      ta.remove(); finish();
    }
  }

  function buildTracePrompt(ex, testCase) {
    const linePart = testCase.line && ex.test_path ? ` (${ex.test_path}:${testCase.line})` : "";
    const errPart = testCase.message ? ` Failure: ${testCase.message}` : "";
    return `Use the trace-and-debug skill: help me trace why \`${testCase.name}\`${linePart} failed in \`${ex.stub_path}\` loop-by-loop (with small inputs and breakpoint suggestions, without giving me the solution).${errPart}`;
  }

  function restoreScroll() {
    try {
      const raw = sessionStorage.getItem(SCROLL_KEY);
      if (!raw) return;
      sessionStorage.removeItem(SCROLL_KEY);
      const { y, ts } = JSON.parse(raw);
      if (Date.now() - ts < 6000 && typeof y === "number") {
        requestAnimationFrame(() => window.scrollTo(0, y));
      }
    } catch (_) {}
  }

  async function openInIde(path, line) {
    try {
      const res = await fetch("/api/open", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path, line: line || null }),
      });
      const data = await res.json();
      toast(data.message || (data.ok ? "Opened in IDE" : "Could not open file"));
    } catch (_) {
      toast("Study server unreachable");
    }
  }

  async function triggerTest(mod) {
    try {
      await fetch("/api/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ module: mod }),
      });
    } catch (_) {
      toast("Could not trigger pytest");
    }
  }

  function currentRepoFile() {
    const src = document.body.dataset.sourceFile;
    if (src) return src;
    let p = decodeURIComponent(location.pathname).replace(/^\/+/, "");
    if (!p || p.endsWith("/")) p += "index.html";
    if (!p.startsWith("gpu-labs/") && !p.startsWith("journal/") && !p.startsWith("exercises/") && p !== "README.md" && p !== "GEMINI.md") {
      return "book/" + p;
    }
    return p;
  }

  function formatBadge(mod, running) {
    const r = state.results[mod];
    if (running) return { cls: "study-badge run", text: "running…" };
    if (!r) return { cls: "study-badge", text: "not run" };
    if (r.error && r.total === 0) return { cls: "study-badge fail", text: "syntax / error" };
    if (r.total > 0 && r.passed === r.total) return { cls: "study-badge pass", text: `${r.passed}/${r.total} ✓` };
    return { cls: "study-badge fail", text: `${r.passed}/${r.total}` };
  }

  function mkBtn(label, cls, title, onClick) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "study-ide-btn sm" + (cls ? " " + cls : "");
    b.textContent = label;
    b.title = title;
    b.addEventListener("click", onClick);
    return b;
  }

  function renderCasesInto(container, ex, r) {
    container.replaceChildren();
    if (!r) return;
    if (r.error) {
      const pre = document.createElement("pre");
      pre.className = "study-err-box";
      pre.textContent = r.error;
      container.append(pre);
    }
    for (const c of r.cases || []) {
      const item = document.createElement("div");
      item.className = "study-case " + c.status;
      const mark = document.createElement("span");
      mark.className = "study-case-mark";
      mark.textContent = c.status === "passed" ? "✓" : c.status === "skipped" ? "○" : "✗";
      const cname = document.createElement("span");
      cname.className = "study-case-name";
      cname.textContent = c.name;

      const btns = document.createElement("span");
      btns.className = "study-case-btns";
      if (c.status !== "passed") {
        const traceBtn = mkBtn(
          "Copy trace prompt",
          "trace",
          "Copy a loop-by-loop trace prompt to paste into Antigravity chat",
          () => copyText(buildTracePrompt(ex, c), traceBtn, "Prompt copied ✓"),
        );
        btns.append(traceBtn);
      }
      if (ex.test_path) {
        btns.append(
          mkBtn(
            c.line ? `Debug :L${c.line}` : "Open test",
            "",
            `Jump to ${c.name} in ${ex.test_path}`,
            () => openInIde(ex.test_path, c.line || 1),
          ),
        );
      }
      item.append(mark, cname, btns);

      if (c.status !== "passed" && c.message) {
        const msg = document.createElement("div");
        msg.className = "study-case-msg";
        msg.textContent = c.message;
        item.append(msg);
      }
      if (c.status !== "passed" && c.detail) {
        const det = document.createElement("details");
        det.className = "study-case-trace";
        const sum = document.createElement("summary");
        sum.textContent = "Show traceback & local variables";
        const pre = document.createElement("pre");
        pre.textContent = c.detail;
        det.append(sum, pre);
        item.append(det);
      }
      container.append(item);
    }
  }

  function injectTopbarAndSidebar() {
    const topbar = document.querySelector("header.topbar");
    if (topbar && !topbar.querySelector(".study-pill")) {
      statusPill = document.createElement("span");
      statusPill.className = "study-pill";
      statusPill.title = "Study Cockpit live reload & auto-pytest on save";
      statusPill.innerHTML = '<span class="study-dot"></span><span>Live</span>';

      const editBtn = mkBtn("Edit in IDE", "", `Open ${currentRepoFile()} in Antigravity IDE`, () => openInIde(currentRepoFile()));

      const spacer = topbar.querySelector(".spacer");
      if (spacer) spacer.after(statusPill, editBtn);
      else topbar.append(statusPill, editBtn);
    }

    // Add breadcrumb when viewing rendered Markdown / GPU Labs / Journal
    if (document.body.dataset.page === "lab") {
      const crumbs = document.querySelector("header.topbar nav.crumbs");
      if (crumbs && !crumbs.children.length) {
        const src = currentRepoFile();
        const sep = () => { const s = document.createElement("span"); s.className = "sep"; s.textContent = "/"; return s; };
        if (src.startsWith("gpu-labs/")) {
          const link = document.createElement("a");
          link.href = "/gpu-labs/README.md";
          link.textContent = "Cloud GPU Labs";
          crumbs.append(sep(), link);
          if (src !== "gpu-labs/README.md") {
            const cur = document.createElement("span");
            cur.className = "cur";
            cur.textContent = src.slice(9).replace(/\/README\.md$/, "");
            crumbs.append(sep(), cur);
          }
        } else {
          const cur = document.createElement("span");
          cur.className = "cur";
          cur.textContent = src;
          crumbs.append(sep(), cur);
        }
      }
    }

    // Add Cloud GPU Labs link to sidebar nav
    const nav = document.querySelector("aside.sidebar .nav");
    if (nav && !nav.querySelector("[data-study-labs-link]")) {
      const refLink = nav.querySelector('a[href*="reference-cheatsheet.html"]');
      const labLink = document.createElement("a");
      labLink.className = "nav-link" + (location.pathname.startsWith("/gpu-labs/") ? " active" : "");
      labLink.href = "/gpu-labs/README.md";
      labLink.dataset.studyLabsLink = "1";
      const ic = window.SWEicon ? window.SWEicon("play") : document.createTextNode("▸ ");
      labLink.append(ic, "Cloud GPU Labs");
      if (refLink) refLink.after(labLink);
      else nav.prepend(labLink);
    }
  }

  function wireGlobalHelpers() {
    document.querySelectorAll('input[type="checkbox"][data-md-check]').forEach((cb) => {
      const key = "md-check:" + cb.dataset.mdCheck;
      const saved = store.get(key, null);
      if (saved !== null) cb.checked = !!saved;
      const row = cb.closest(".check-row");
      if (row) row.classList.toggle("checked", cb.checked);
      cb.addEventListener("change", () => {
        store.set(key, cb.checked);
        if (row) row.classList.toggle("checked", cb.checked);
      });
    });

    document.querySelectorAll(".study-code-wrap .study-code-copy").forEach((btn) => {
      btn.addEventListener("click", () => {
        const code = btn.parentElement.querySelector("pre code")?.textContent || "";
        copyText(code, btn, "Copied");
      });
    });

    // Intercept data-ide-open and any local links to exercises/*.py so they open directly in Antigravity IDE
    document.addEventListener("click", (e) => {
      const a = e.target.closest("a");
      if (!a) return;
      if (a.dataset.ideOpen) {
        e.preventDefault();
        openInIde(a.dataset.ideOpen, Number(a.dataset.ideLine) || null);
        return;
      }
      const raw = a.getAttribute("href") || "";
      if (/^(?:\.\.\/|\/)*exercises\/.+\.py$/i.test(raw)) {
        e.preventDefault();
        const rel = raw.replace(/^(?:\.\.\/|\/)+/, "");
        openInIde(rel);
      }
    });
  }

  function enhanceExistingExerciseLinks() {
    const page = document.body.dataset.page || "";
    const secId = document.body.dataset.section || "";

    if (page === "chapter" && secId) {
      document.querySelectorAll('main a[href*="exercises/"]').forEach((a) => {
        if (a.dataset.studyWired) return;
        const fname = (a.getAttribute("href") || "").split("/").pop();
        if (!fname || !fname.endsWith(".py")) return;
        const mod = fname.replace(/\.py$/, "");
        const meta = state.exercises[mod];
        if (!meta) return;
        a.dataset.studyWired = "1";
        a.dataset.ideOpen = meta.stub_path;
        a.title = `Open ${meta.stub_path} in Antigravity IDE`;

        const tr = a.closest("tr");
        if (!tr) return;
        const cells = tr.querySelectorAll("td");
        if (cells.length >= 4) {
          cells[2].dataset.studyStatusMod = mod;
          const wrap = document.createElement("span");
          wrap.className = "study-tbl-actions";
          wrap.append(mkBtn("Code", "primary", `Open ${meta.stub_path} in IDE`, () => openInIde(meta.stub_path)));
          if (meta.test_path) {
            wrap.append(mkBtn("Tests", "", `Open ${meta.test_path} in IDE (for Debug Test)`, () => openInIde(meta.test_path)));
          }
          wrap.append(mkBtn("Run", "", `Run pytest on ${mod}`, () => triggerTest(mod)));
          cells[3].replaceChildren(wrap);
        }
      });
    }

    if (page === "home") {
      document.querySelectorAll("a.ex-chip").forEach((chip) => {
        if (chip.dataset.studyWired) return;
        const codeEl = chip.querySelector("code");
        if (!codeEl) return;
        const mod = codeEl.textContent.trim();
        const meta = state.exercises[mod];
        if (!meta) return;
        chip.dataset.studyWired = "1";
        chip.dataset.ideOpen = meta.stub_path;
        chip.title = `Open ${meta.stub_path} in Antigravity IDE (save to auto-run pytest)`;
        chip.dataset.studyChipMod = mod;
      });
    }
  }

  function chapterExercises() {
    const topicMeta = document.querySelector('meta[name="topic"]');
    if (!topicMeta) return [];
    const tid = topicMeta.content.trim();
    return Object.values(state.exercises).filter((ex) => (ex.topics || []).includes(tid));
  }

  function renderChapterDock(runningMod = null) {
    if (document.body.dataset.page !== "concept") return;
    const exs = chapterExercises();
    if (!exs.length) return;

    let dock = document.getElementById("study-chapter-dock");
    if (!dock) {
      const head = document.querySelector("main.book header.chapter-head");
      if (!head) return;
      dock = document.createElement("section");
      dock.id = "study-chapter-dock";
      dock.className = "study-dock";
      head.after(dock);
    }

    dock.replaceChildren();
    const header = document.createElement("div");
    header.className = "study-dock-head";
    header.innerHTML =
      '<span class="study-dock-title">IDE Exercise Cockpit</span>' +
      '<span class="study-dock-tip">Save to auto-run pytest · Drop a breakpoint in your loop &amp; press <kbd>F5</kbd> for live inline values</span>';
    dock.append(header);

    for (const ex of exs) {
      const mod = ex.module;
      const r = state.results[mod];
      const isRunning = runningMod === mod;
      const badgeInfo = formatBadge(mod, isRunning);
      const hasFailures = r && (r.error || (r.cases && r.cases.some((c) => c.status !== "passed")));
      if (hasFailures && !openDetails.has(mod + ":manual-closed")) openDetails.add(mod);

      const row = document.createElement("div");
      row.className = "study-ex-row";

      const main = document.createElement("div");
      main.className = "study-ex-main";

      const nameEl = document.createElement("span");
      nameEl.className = "study-ex-mod";
      nameEl.textContent = mod + ".py";

      const badge = document.createElement("span");
      badge.className = badgeInfo.cls;
      badge.textContent = badgeInfo.text;

      const actions = document.createElement("div");
      actions.className = "study-ex-actions";
      actions.append(mkBtn("Open .py", "primary", `Open ${ex.stub_path} in Antigravity IDE`, () => openInIde(ex.stub_path)));
      if (ex.test_path) {
        actions.append(mkBtn("Open tests", "", `Open ${ex.test_path} in Antigravity IDE`, () => openInIde(ex.test_path)));
      }
      actions.append(mkBtn(isRunning ? "Running…" : "Run pytest", "", `Run pytest for ${mod}`, () => triggerTest(mod)));

      const casesBox = document.createElement("div");
      casesBox.className = "study-cases";
      const showCases = openDetails.has(mod) && r && (r.error || (r.cases && r.cases.length > 0));
      casesBox.hidden = !showCases;

      if (r && (r.error || (r.cases && r.cases.length > 0))) {
        const toggleBtn = mkBtn(showCases ? "Hide tests" : "Tests", "", "Show per-test results, Copy trace prompt, and Debug jump lines", () => {
          const nextOpen = casesBox.hidden;
          casesBox.hidden = !nextOpen;
          toggleBtn.textContent = nextOpen ? "Hide tests" : "Tests";
          if (nextOpen) {
            openDetails.add(mod);
            openDetails.delete(mod + ":manual-closed");
          } else {
            openDetails.delete(mod);
            openDetails.add(mod + ":manual-closed");
          }
        });
        actions.append(toggleBtn);
        renderCasesInto(casesBox, ex, r);
      }

      main.append(nameEl, badge, actions);
      row.append(main, casesBox);
      dock.append(row);
    }
  }

  function activeStickyModule(runningMod) {
    const mod = runningMod || state.last_module || store.get("study-last-ex", null);
    if (!mod || !state.exercises[mod]) return null;
    // Skip redundant sticky bar when that exact exercise is already docked on this chapter page
    if (document.body.dataset.page === "concept") {
      const onThisChapter = chapterExercises().some((ex) => ex.module === mod);
      if (onThisChapter && !stickyDrawerOpen) return null;
    }
    return mod;
  }

  function renderStickyBar(runningMod = null) {
    const existing = document.getElementById("study-sticky-bar");
    const mod = stickyDismissed ? null : activeStickyModule(runningMod);
    if (!mod) {
      existing?.remove();
      document.body.classList.remove("has-study-bar");
      return;
    }
    const ex = state.exercises[mod];
    const r = state.results[mod];
    const isRunning = runningMod === mod;
    const badgeInfo = formatBadge(mod, isRunning);

    let bar = existing;
    if (!bar) {
      bar = document.createElement("aside");
      bar.id = "study-sticky-bar";
      bar.className = "study-sticky";
      bar.setAttribute("aria-label", "Last saved exercise status");
      document.body.append(bar);
    }
    document.body.classList.add("has-study-bar");
    bar.replaceChildren();

    const drawer = document.createElement("div");
    drawer.className = "study-sticky-drawer";
    const hasDetails = r && (r.error || (r.cases && r.cases.length > 0));
    drawer.hidden = !(stickyDrawerOpen && hasDetails);
    if (hasDetails) renderCasesInto(drawer, ex, r);

    const row = document.createElement("div");
    row.className = "study-sticky-row";

    const tag = document.createElement("span");
    tag.className = "study-sticky-tag";
    tag.textContent = "Last exercise";

    const name = document.createElement("span");
    name.className = "study-ex-mod";
    name.textContent = mod + ".py";

    const badge = document.createElement("span");
    badge.className = badgeInfo.cls;
    badge.textContent = badgeInfo.text;

    const actions = document.createElement("div");
    actions.className = "study-ex-actions";
    actions.append(mkBtn("Open .py", "primary", `Open ${ex.stub_path} in IDE`, () => openInIde(ex.stub_path)));
    if (ex.test_path) {
      actions.append(mkBtn("Tests", "", `Open ${ex.test_path} in IDE`, () => openInIde(ex.test_path)));
    }
    actions.append(mkBtn(isRunning ? "Running…" : "Run", "", `Re-run pytest for ${mod}`, () => triggerTest(mod)));
    if (hasDetails) {
      const firstFail = (r.cases || []).find((c) => c.status !== "passed");
      if (firstFail) {
        const tBtn = mkBtn(
          "Copy trace prompt",
          "trace",
          `Copy loop-trace prompt for ${firstFail.name}`,
          () => copyText(buildTracePrompt(ex, firstFail), tBtn, "Prompt copied ✓"),
        );
        actions.append(tBtn);
      }
      actions.append(
        mkBtn(stickyDrawerOpen ? "▼ Hide" : "▲ Details", "", "Toggle per-test breakdown", () => {
          stickyDrawerOpen = !stickyDrawerOpen;
          renderStickyBar(runningMod);
        }),
      );
    }
    actions.append(
      mkBtn("×", "", "Dismiss until next exercise save", () => {
        stickyDismissed = true;
        stickyDrawerOpen = false;
        renderStickyBar(null);
      }),
    );

    row.append(tag, name, badge, actions);
    bar.append(drawer, row);
  }

  function paintAllBadges(runningMod = null) {
    document.querySelectorAll("[data-study-status-mod]").forEach((td) => {
      const mod = td.dataset.studyStatusMod;
      const info = formatBadge(mod, runningMod === mod);
      td.innerHTML = `<span class="${info.cls}">${info.text}</span>`;
    });

    document.querySelectorAll("a[data-study-chip-mod]").forEach((chip) => {
      const mod = chip.dataset.studyChipMod;
      const r = state.results[mod];
      const existing = chip.querySelector(".test-pass, .test-fail, .test-none");
      if (runningMod === mod) {
        if (existing) { existing.className = "test-none"; existing.textContent = "…"; }
        return;
      }
      if (!r || !r.total) return;
      const span = existing || document.createElement("span");
      span.className = r.passed === r.total ? "test-pass" : "test-fail";
      span.textContent = `${r.passed}/${r.total}`;
      if (!existing) chip.append(span);
    });

    renderChapterDock(runningMod);
    renderStickyBar(runningMod);
  }

  function connectSSE() {
    const es = new EventSource("/api/events");
    es.onopen = () => {
      if (statusPill) {
        statusPill.className = "study-pill";
        statusPill.lastElementChild.textContent = "Live";
      }
    };
    es.onerror = () => {
      if (statusPill) {
        statusPill.className = "study-pill offline";
        statusPill.lastElementChild.textContent = "Reconnecting…";
      }
    };
    es.addEventListener("reload", (ev) => {
      let info = {};
      try { info = JSON.parse(ev.data || "{}"); } catch (_) {}
      try { sessionStorage.setItem(SCROLL_KEY, JSON.stringify({ y: window.scrollY, ts: Date.now() })); } catch (_) {}
      toast(info.path ? `Updated ${info.path} — reloading…` : "Updated — reloading…", 900);
      setTimeout(() => location.reload(), 160);
    });
    es.addEventListener("test-running", (ev) => {
      const data = JSON.parse(ev.data || "{}");
      state.last_module = data.module;
      store.set("study-last-ex", data.module);
      stickyDismissed = false;
      if (statusPill) {
        statusPill.className = "study-pill running";
        statusPill.lastElementChild.textContent = `Testing ${data.module}…`;
      }
      paintAllBadges(data.module);
    });
    es.addEventListener("test-result", (ev) => {
      const res = JSON.parse(ev.data || "{}");
      state.results[res.module] = res;
      state.last_module = res.module;
      store.set("study-last-ex", res.module);
      stickyDismissed = false;
      if (statusPill) {
        statusPill.className = "study-pill";
        statusPill.lastElementChild.textContent = "Live";
      }
      paintAllBadges(null);
      if (res.error && res.total === 0) {
        toast(`${res.module}: error — check Cockpit`, 2600);
      } else if (res.passed === res.total && res.total > 0) {
        toast(`${res.module}: ${res.passed}/${res.total} passed ✓`, 2400);
      } else {
        toast(`${res.module}: ${res.passed}/${res.total} passing`, 2200);
      }
    });
  }

  async function boot() {
    restoreScroll();
    injectTopbarAndSidebar();
    wireGlobalHelpers();
    try {
      const res = await fetch("/api/state", { cache: "no-store" });
      state = await res.json();
      if (state.last_module) store.set("study-last-ex", state.last_module);
    } catch (_) {}
    enhanceExistingExerciseLinks();
    paintAllBadges(null);
    connectSSE();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => setTimeout(boot, 0));
  } else {
    setTimeout(boot, 0);
  }
})();
"""


def inject_cockpit(raw_html: bytes, source_rel: str | None = None) -> bytes:
    """Inject Study Cockpit CSS & JS dynamically at serve time (static files stay untouched)."""
    text = raw_html.decode("utf-8", errors="replace")
    css_tag = '  <link rel="stylesheet" href="/__study/cockpit.css">\n'
    js_tag = '<script src="/__study/cockpit.js"></script>\n'
    if source_rel and "data-source-file=" not in text:
        esc = html_mod.escape(source_rel, quote=True)
        text = re.sub(r"<body\b", f'<body data-source-file="{esc}"', text, count=1)
    if "</head>" in text:
        text = text.replace("</head>", css_tag + "</head>", 1)
    else:
        text = css_tag + text
    if "</body>" in text:
        text = text.replace("</body>", js_tag + "</body>", 1)
    else:
        text = text + js_tag
    return text.encode("utf-8")


# ---------------------------------------------------------------------------
# Polling File Watcher (zero third-party dependencies)
# ---------------------------------------------------------------------------

def snapshot_mtimes() -> dict[str, float]:
    mtimes: dict[str, float] = {}
    roots = [BOOK_ROOT, EX_ROOT, LABS_ROOT, JOURNAL_ROOT]
    top_files = [ROOT / "curriculum.json", ROOT / "README.md", ROOT / "GEMINI.md"]
    for f in top_files:
        if f.is_file():
            try:
                mtimes[f.relative_to(ROOT).as_posix()] = f.stat().st_mtime
            except OSError:
                pass
    for r in roots:
        if not r.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(r):
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
            for fn in filenames:
                if fn.startswith(".") or fn.endswith((".pyc", ".swp", "~")):
                    continue
                fp = Path(dirpath) / fn
                try:
                    mtimes[fp.relative_to(ROOT).as_posix()] = fp.stat().st_mtime
                except OSError:
                    pass
    return mtimes


def start_watcher(state: CockpitState, interval: float = 0.35) -> threading.Thread:
    def _loop() -> None:
        prev = snapshot_mtimes()
        while True:
            time.sleep(interval)
            cur = snapshot_mtimes()
            changed = [p for p, mt in cur.items() if prev.get(p) != mt]
            removed = [p for p in prev if p not in cur]
            prev = cur
            if not changed and not removed:
                continue

            py_mods: set[str] = set()
            reload_target: str | None = None
            rebuild_curriculum = False

            for rel in changed + removed:
                p = Path(rel)
                if rel == "curriculum.json":
                    rebuild_curriculum = True
                    reload_target = rel
                elif p.suffix == ".py" and len(p.parts) >= 3 and p.parts[0] == "exercises":
                    stem = p.stem
                    mod = stem[5:] if stem.startswith("test_") else stem
                    if mod != "conftest" and not mod.startswith("_"):
                        py_mods.add(mod)
                elif p.suffix in (".html", ".md", ".css", ".js", ".svg"):
                    reload_target = rel

            if rebuild_curriculum:
                subprocess.run([resolve_python(), str(ROOT / "tools" / "build.py")], cwd=ROOT)
                state.refresh_index()

            if py_mods:
                state.refresh_index()
                for mod in sorted(py_mods):
                    threading.Thread(target=state.run_module_tests, args=(mod,), daemon=True).start()

            if reload_target:
                state.refresh_index()
                state.hub.broadcast("reload", {"path": reload_target})

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t


# ---------------------------------------------------------------------------
# HTTP Request Handler
# ---------------------------------------------------------------------------

def resolve_route(route: str) -> Path | None:
    """Resolve web route to a real file in book/ (default) or mounted repo dirs."""
    clean = urllib.parse.unquote(route)
    if clean in ("", "/"):
        return BOOK_ROOT / "index.html"
    if clean in ("/gpu-labs", "/gpu-labs/", "/labs", "/labs/"):
        return LABS_ROOT / "README.md"

    # Explicit top-level repo mounts (Markdown labs, journals, docs, exercises)
    stripped = clean.lstrip("/")
    if stripped.startswith(("gpu-labs/", "journal/", "exercises/")) or stripped in ("README.md", "GEMINI.md"):
        cand = safe_repo_path(stripped)
        if cand is None:
            return None
        if cand.is_dir():
            for name in ("README.md", "index.html"):
                if (cand / name).is_file():
                    return cand / name
            return None
        return cand if cand.is_file() else None

    # Default: serve from book/ (mirrors GitHub Pages root)
    cand = safe_path_under(BOOK_ROOT, stripped)
    if cand is None:
        return None
    if cand.is_dir():
        idx = cand / "index.html"
        return idx if idx.is_file() else None
    return cand if cand.is_file() else None


def make_handler(state: CockpitState, host: str, port: int):
    allowed_hosts = {f"{host}:{port}", f"localhost:{port}", f"127.0.0.1:{port}"}

    class StudyHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt: str, *args) -> None:
            return

        def _send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, obj: dict, status: int = 200) -> None:
            self._send_bytes(json.dumps(obj).encode("utf-8"), "application/json; charset=utf-8", status)

        def _check_same_origin(self) -> bool:
            origin = self.headers.get("Origin")
            if origin:
                parsed = urllib.parse.urlparse(origin)
                if parsed.netloc not in allowed_hosts:
                    return False
            return True

        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            route = parsed.path

            if route == "/__study/cockpit.css":
                self._send_bytes(COCKPIT_CSS.encode("utf-8"), "text/css; charset=utf-8")
                return
            if route == "/__study/cockpit.js":
                self._send_bytes(COCKPIT_JS.encode("utf-8"), "application/javascript; charset=utf-8")
                return
            if route == "/api/state":
                self._send_json(state.snapshot())
                return
            if route == "/api/events":
                self._handle_sse()
                return

            target = resolve_route(route)
            if target is None or not target.is_file():
                self._send_bytes(b"Not found", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
                return

            suffix = target.suffix.lower()
            try:
                if suffix == ".md":
                    body = render_markdown_page(target, state)
                    self._send_bytes(body, "text/html; charset=utf-8")
                    return
                raw = target.read_bytes()
            except OSError:
                self._send_bytes(b"Read error", "text/plain; charset=utf-8", HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            if suffix in (".html", ".htm"):
                rel = target.relative_to(ROOT).as_posix()
                self._send_bytes(inject_cockpit(raw, source_rel=rel), "text/html; charset=utf-8")
                return

            ctype, _ = mimetypes.guess_type(target.name)
            if not ctype:
                ctype = "application/octet-stream"
            elif ctype.startswith("text/") or ctype in ("application/javascript", "application/json", "image/svg+xml"):
                ctype += "; charset=utf-8"
            self._send_bytes(raw, ctype)

        def do_POST(self) -> None:
            if not self._check_same_origin():
                self._send_json({"ok": False, "message": "Forbidden origin"}, HTTPStatus.FORBIDDEN)
                return
            parsed = urllib.parse.urlparse(self.path)
            length = int(self.headers.get("Content-Length") or "0")
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except (ValueError, UnicodeDecodeError):
                self._send_json({"ok": False, "message": "Invalid JSON"}, HTTPStatus.BAD_REQUEST)
                return

            if parsed.path == "/api/open":
                rel = str(payload.get("path") or "")
                line = payload.get("line")
                target = safe_repo_path(rel)
                if not target or not target.is_file():
                    self._send_json({"ok": False, "message": f"File not found: {rel}"}, HTTPStatus.NOT_FOUND)
                    return
                ok, msg = open_in_ide(target, int(line) if isinstance(line, int) else None)
                self._send_json({"ok": ok, "message": msg}, HTTPStatus.OK if ok else HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            if parsed.path == "/api/test":
                mod = str(payload.get("module") or "").strip()
                if mod == "__all__":
                    state.run_all_tests_async()
                    self._send_json({"ok": True, "queued": "all"})
                    return
                if mod not in state.exercises:
                    state.refresh_index()
                if mod not in state.exercises:
                    self._send_json({"ok": False, "message": f"Unknown module: {mod}"}, HTTPStatus.NOT_FOUND)
                    return
                threading.Thread(target=state.run_module_tests, args=(mod,), daemon=True).start()
                self._send_json({"ok": True, "queued": mod})
                return

            self._send_json({"ok": False, "message": "Unknown endpoint"}, HTTPStatus.NOT_FOUND)

        def _handle_sse(self) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q = state.hub.subscribe()
            try:
                self.wfile.write(b": connected\n\n")
                self.wfile.flush()
                while True:
                    try:
                        event, data = q.get(timeout=20.0)
                        msg = f"event: {event}\ndata: {json.dumps(data)}\n\n".encode("utf-8")
                        self.wfile.write(msg)
                        self.wfile.flush()
                    except queue.Empty:
                        self.wfile.write(b": keepalive\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                state.hub.unsubscribe(q)

    return StudyHandler


def main() -> None:
    parser = argparse.ArgumentParser(description="gpu/lab Local Study Cockpit server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument("--no-watch", action="store_true", help="Disable background file watcher")
    args = parser.parse_args()

    state = CockpitState()
    if not args.no_watch:
        start_watcher(state)

    server = ThreadingHTTPServer((args.host, args.port), make_handler(state, args.host, args.port))
    server.daemon_threads = True

    editor = resolve_editor_cmd()
    editor_label = Path(editor[0]).name if editor else "fallback (open)"
    print(f"gpu/lab Study Cockpit ready at http://{args.host}:{args.port}", flush=True)
    print(f"  Book: book/ · Exercises: {len(state.exercises)} · GPU Labs: {len(state.labs)} · IDE CLI: {editor_label}", flush=True)
    print(f"  In Antigravity IDE: Cmd+Shift+P -> Simple Browser: Show -> http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStudy Cockpit stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
