---
name: visuals-and-layout
description: Design and verify visual diagrams and interactive assets/viz.js widgets for a gpu-lab chapter across all four themes and mobile widths.
---

# Visuals, then layout (`gpu/lab`)

1. **Early visual rule:** every chapter puts its first visual (SVG, `.diagram`,
   or interactive `.figure`) in Section 1 or 2.
2. **No visual deserts:** never more than 2 consecutive sections without a visual.
3. **Theme tokens only:** use `var(--accent)`, `--accent-2`, `--ok`, `--warn`,
   `--bad`, `--brand`, `--surface`, `--surface-2`, `--border`, `--text`,
   `--muted` so Ayu Dark, Ayu Mirage, Gruvbox Dark Hard, and Ayu Light all work.
4. **Interactive widgets with `assets/viz.js`:** `V.player` steppers for forward
   passes, LoRA merging, token masking, and barge-in frames; sliders for VRAM
   scaling and latency budgets. Wrap every widget in `.figure` with a `.cap`
   telling the reader what to press and notice.
5. **Layout check:** verify desktop (1280px) and phone (390px) have zero
   horizontal overflow, tables sit inside `.table-wrap`, code blocks stay ≤15
   lines where possible, and `node tools/check_page.js <page>` (when Playwright
   is available) reports clean.
