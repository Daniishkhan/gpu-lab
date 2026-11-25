# `gpu/lab` HTML Component Reference

Every chapter in `sections/<NN>/concepts/<slug>.html` must work **100% offline over `file://`** with zero external CDNs, fonts, images, or `fetch()` calls, and across all four themes (Ayu Dark, Ayu Mirage, Gruvbox Dark Hard, Ayu Light).

## 1. Document Shell & Head

```html
<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="topic" content="01.01">
  <!-- Remove <meta name="status" content="outline"> once the chapter is complete -->
  <title>Chapter Title</title>
  <script>try { document.documentElement.dataset.theme = JSON.parse(localStorage.getItem("gpu-lab:theme")) || "dark"; } catch (e) {}</script>
  <link rel="stylesheet" href="../../../assets/style.css">
  <script src="../../../assets/curriculum.js"></script>
  <script src="../../../assets/viz.js"></script>
  <script src="../../../assets/shell.js"></script>
  <script src="../../../assets/book.js"></script>
</head>
<body data-root="../../.." data-section="01" data-page="concept">
<main class="content book">
  ...
</main>
<script>
(function () {
  // Interactive visuals using window.V (assets/viz.js).
})();
</script>
</body>
</html>
```

## 2. Header, Learning List & Prerequisite Link Line

- `tools/build.py` checks links inside the `How to read this` paragraph against `requires` in `curriculum.json`. Every concept linked inside that `<p>` **must** appear in the topic's `requires` array.

```html
<header class="chapter-head">
  <div class="eyebrow">Stage X · Subject NN · Section Title</div>
  <h1>Chapter Title</h1>
  <div class="meta">
    <span><span class="badge P0">P0</span> Short role tag</span>
    <span>about 15 minutes</span>
    <span>6 quick checks · 1 CPU exercise</span>
  </div>
</header>

<p>Two to three plain sentences explaining why this matters — zero unintroduced jargon.</p>

<div class="learn-list">
  <h4>By the end you'll be able to</h4>
  <ol>
    <li>Concrete capability #1…</li>
    <li>Concrete capability #2…</li>
  </ol>
</div>

<p class="muted small">How to read this: top to bottom, answering every quick check before moving on. Builds on <a href="prior-chapter.html">Prior Chapter Title</a>.</p>
```

## 3. Section Headings & Core Prose Blocks

Every `<h2>` inside `<main>` **must** have an `id` (`s1`, `s2`, …, `summary`, `exercises`) so the right-hand TOC rail links properly.

```html
<h2 id="s1"><span class="sec-num">1</span>Question-led section title?</h2>

<div class="story">
  <p>Concrete pain, toy breakdown, or real OOM/latency scenario with small numbers.</p>
</div>

<div class="keyidea"><b>Memorable rule name:</b> One or two crisp sentences capturing the core invariant.</div>

<!-- Callouts: default (accent), .warn, .bad, .ok -->
<div class="callout warn"><b>Where this analogy breaks:</b> Exact limit where the physical anchor diverges from silicon or math.</div>
```

## 4. Visual Figures, Diagrams & Tables

- Every `.figure` **must** contain a `.cap` telling the reader what to press, trace, or notice.
- Every `<table>` **must** sit inside `<div class="table-wrap">` so phone viewports (390px) scroll cleanly inside the table rather than overflowing the page.
- Keep `<pre><code>` blocks ≤15 lines; use `<pre class="plain"><code>` for shell commands and `<pre class="diagram"><code>` for ASCII diagrams (`shell.js` syntax-highlights Python inside plain `<pre><code>`).

```html
<div class="figure">
  <svg class="viz" viewBox="0 0 720 220" role="img" aria-label="Accessible description of diagram">
    <!-- Use CSS var(--*) tokens ONLY; never hardcode hex colors -->
  </svg>
  <div class="cap">What to look for in this diagram.</div>
</div>

<div class="figure">
  <div id="viz-example"></div>
  <div class="cap">Press <b>Next</b> or drag the slider to watch X change Y.</div>
</div>

<div class="table-wrap"><table>
  <thead><tr><th>Col A</th><th>Col B</th></tr></thead>
  <tbody><tr><td><code>val</code></td><td>Explanation</td></tr></tbody>
</table></div>
```

## 5. Collapsible Asides (Protect the Core Path)

```html
<details class="aside deeper">
  <summary>Go deeper: Algebraic derivation or secondary production edge case</summary>
  <p>Stays collapsed by default so first-pass reading stays fast and clear.</p>
</details>

<details class="aside another">
  <summary>Explain it another way: Geometric intuition</summary>
  <p>Alternative angle for learners who want a second mental picture.</p>
</details>
```

## 6. Quick Checks (`.check` — wired automatically by `assets/book.js`)

- `id` **must** start with `check-` and be unique across the page.
- **Exactly one** button inside `.opts` has `data-correct`.
- Must include **both** `.fb.right` and `.fb.wrong`.

```html
<div class="check" id="check-unique-slug">
  <p class="q">Prediction or failure-mode question?</p>
  <div class="opts">
    <button>Plausible misconception A</button>
    <button data-correct>Correct causal prediction with concise reasoning</button>
    <button>Plausible misconception B</button>
  </div>
  <div class="fb right"><p>Reinforces why the mechanism produces this result.</p></div>
  <div class="fb wrong"><p>Re-explains the core mechanism from a different angle without repeating the right feedback.</p></div>
</div>
```

## 7. Summary, Review, Exercises & Navigation

```html
<h2 id="summary"><span class="sec-num">✓</span>What to remember</h2>
<ol>
  <li>Crisp engineering takeaway with exact numbers/units…</li>
</ol>

<div class="review" id="review"></div>

<h2 id="exercises"><span class="sec-num">✎</span>Exercises</h2>

<div class="exercise">
  <div class="tier warm">Warm-up · interactive workbench</div>
  <h4>Explore the numbers in <code>workbench.html</code></h4>
  <p>Open <a href="../../../workbench.html">workbench.html</a> and compare…</p>
</div>

<div class="exercise">
  <div class="tier core">Core · local CPU code (pytest)</div>
  <h4>Implement <code>module_name.py</code></h4>
  <p>Open <a href="../exercises/module_name.py"><code>module_name.py</code></a> and verify with:</p>
  <pre class="plain"><code>python3 -m pytest -k module_name</code></pre>
</div>

<nav class="chapter-nav">
  <a href="prev-chapter.html"><small>← Previous</small>Previous Chapter Title</a>
  <a class="next" href="next-chapter.html"><small>Next →</small>Next Chapter Title</a>
</nav>
```

## 8. HTML Escaping Pitfalls

- Always write `<code>&lt;|turn&gt;user</code>` and `<code>&lt;turn|&gt;</code>` — raw `<|turn>` or `<turn|>` corrupts the DOM!
- Always write `&lt;`, `&gt;`, `&amp;` in prose and SVG text (e.g., `&lt;800 ms`, `Q &amp; K`).
- Never write markdown backticks (`` `x` ``) or asterisks (`**x**`) inside HTML prose — use `<code>x</code>` and `<b>x</b>`.
