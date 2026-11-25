# Cloud GPU Runbook: {{TITLE}}

- **Date:** {{DATE}}
- **Recommended GPU:** (e.g., `1× NVIDIA L4 24GB` on RunPod / Modal / Colab Pro)
- **Estimated VRAM / Runtime / Cost:** `~XX GB` · `~XX min` · `~$X.XX`

## Pre-Flight Checks (do on CPU before renting)
- [ ] Verified VRAM budget in `workbench.html`
- [ ] Dataset formatting & loss masking unit tests pass locally
- [ ] Hugging Face token & pinned package versions ready

## 1. Environment Setup
```bash
# Pinned versions go here
```

## 2. Run & Verify
```bash
# Reproducible script / CLI command
```

## 3. Production Gotchas to Watch
- Gotcha 1:
- Gotcha 2:

## 4. Teardown & Save Artifacts
- [ ] Saved adapter/merged weights + eval JSON to object storage or HF Hub
- [ ] Shut down GPU pod immediately
