---
name: visuals-and-layout
description: Design and verify intuition-building SVG diagrams and interactive assets/viz.js widgets for gpu/lab chapters across all four themes and desktop/mobile widths.
---

# Visuals, Interactive Widgets & Layout (`gpu/lab`)

Visuals in `gpu/lab` are **not decoration** — they are the primary way a learner builds physical and geometric intuition before seeing formal equations or PyTorch code.

## 1. Visual Pedagogy Rules

1. **Carry real explanatory weight:** Every SVG, `pre.diagram`, or interactive widget must show at least one of:
   - *Spatial / tensor shape alignment* (e.g., `(B, T, D_in) @ (D_in, D_out)`, GQA head sharing, RVQ codebook layers),
   - *Change over time* (`V.player` stepper for forward/backward passes, BPE merges, attention masking, LoRA merge, KV cache growth, barge-in flush),
   - *Causal knob → effect* (interactive sliders/toggles for roofline utilization, VRAM stack bars, quantization rounding error, `<800 ms` latency budget).
   Ban empty "boxes with arrows" that merely repeat a bulleted list.
2. **Early visual & no visual deserts:**
   - Put the first visual in Section 1 or 2 (`#s1` or `#s2`).
   - Leave **at most 2 consecutive numbered `h2` sections** without a visual (`.figure`, `<svg>`, or `pre.diagram`).
3. **Every `.figure` needs a directive `.cap`:** Tell the reader *what to press or compare* and *what surprising behavior to notice* — never a generic label like "Figure 1: Diagram of X".

## 2. Using `assets/viz.js` (`window.V`)

Everything runs offline with zero external libraries. Available primitives in `assets/viz.js`:

| Helper | Purpose |
|---|---|
| `V.el(tag, attrs, ...children)` | Create HTML element (`class`, `text`, `html`, `on*` listeners supported) |
| `V.s(tag, attrs, ...children)` | Create SVG element in the SVG namespace |
| `V.cells(values, { cls, ptrs, idx, label })` | Row of indexed array/token cells with pointer badges and highlight classes (`hl`, `win`, `bad`, `warn`, `dim`, `cmp`, `pivot`, `done`, `empty`) |
| `V.player(box, { frames, draw, speed, extraControls })` | Step-through player with First / Prev / Play / Next / Speed controls; `frame.msg` renders as caption HTML |
| `V.binaryTree(svg, root, opts)` | Auto-laid-out binary tree into `<svg class="viz">` |
| `V.graph(svg, nodes, edges, opts)` | Directed/undirected computation graph (ideal for autograd backprop, attention links, model chains) |

### Interactive Widget Patterns That Work Well
- **Step-through trace (`V.player`):** Precompute 5–12 deterministic `frames` with tiny concrete numbers (e.g., 3-node autograd forward + backward blame flow, 4-token causal attention mask, token-by-token `-100` loss masking). Highlight active cells/nodes with `hl` / `warn` / `ok` and explain *why* in `frame.msg`.
- **Live parameter explorer:** Pair mode buttons (`btn` / `btn primary`) or `<input type="range" style="accent-color:var(--accent)">` with live stacked bars, KPI tiles (`background:var(--surface-2);border:1px solid var(--border)`), and a clear threshold/regime banner.
- Guard every inline script with `if (!host || !window.V) return;` and wrap inside an IIFE `(function () { ... })();` so globals never collide.

## 3. Four-Theme Color & Contrast Contract

Pages support **Ayu Dark** (`dark`), **Ayu Mirage** (`mirage`), **Gruvbox Dark Hard** (`gruvbox`), and **Ayu Light** (`light`).

- **Zero hardcoded colors** (`#fff`, `#000`, `rgb(...)`, named colors) in SVGs or inline styles.
- Use **only** semantic CSS tokens from `assets/style.css`:
  - Surfaces & borders: `var(--bg)`, `var(--bg-2)`, `var(--surface)`, `var(--surface-2)`, `var(--surface-3)`, `var(--border)`, `var(--border-strong)`
  - Text hierarchy: `var(--text-strong)`, `var(--text)`, `var(--muted)`, `var(--faint)`
  - Semantic accents & soft fills: `var(--brand)`, `var(--accent)`, `var(--accent-2)`, `var(--ok)`, `var(--warn)`, `var(--bad)`, plus `--accent-soft`, `--ok-soft`, `--warn-soft`, `--bad-soft`
  - Text on solid accent/status bars: `var(--on-accent)` (automatically switches dark/light per theme!)
- **Contrast check for Ayu Light:** Never put white/light text on soft fills; use `var(--text-strong)` or the matching semantic color on `var(--*-soft)` backgrounds, and `var(--on-accent)` only on solid `var(--accent)` / `var(--ok)` / `var(--bad)` fills.

## 4. SVG & Responsive Layout Checklist

- Give every inline `<svg>` `class="viz"`, an explicit `viewBox="0 0 W H"` (typically `W = 680–760`), `role="img"`, and a descriptive `aria-label`. Never set fixed pixel widths that exceed 390px on mobile.
- Keep SVG text legible when scaled down to 390px: avoid tiny sub-10px fonts or cramped labels; prefer clean padding and generous vertical rhythm.
- Wrap every `<table>` in `<div class="table-wrap">`.
- Use responsive grids (`grid-template-columns:repeat(auto-fit,minmax(140px,1fr))`) and `flex-wrap:wrap` for widget controls so 390px phone screens have **zero horizontal overflow**.
- Keep `<pre><code>` blocks ≤15 lines and short lines (~75 chars max) so readers aren't scrolling horizontally.

## 5. Verification

1. Always run the offline linter:
   ```bash
   python3 tools/check_chapter.py <page.html>
   ```
2. When Playwright is installed, verify rendered desktop (1280px), phone (390px), all `V.player` frames, and all 4 themes:
   ```bash
   node tools/check_page.js <page.html> [--shots /tmp/shots]
   ```
   If screenshots are captured, inspect both dark and light themes plus phone width for text overlap, clipping, or low contrast before handing off to `review-chapter`.
