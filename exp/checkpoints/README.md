# `exp/checkpoints/` — Model Checkpoint Storage Policy

> **Policy Notice: No Model Weights Committed to Version Control**  
> Checkpoints and model weights (`.ckpt`, `.pt`, `.safetensors`, `.bin`, `.onnx`) must **never** be committed to Git.

## Purpose
Serves as the local target for pretrained or fine-tuned model checkpoints, and documents checkpoint sources, SHA-256 hashes, licenses, and download instructions.

## What Belongs Here
- Markdown documentation detailing checkpoint provenance, download links, SHA-256 verification hashes, and licensing terms (e.g. NVIDIA Open Model License).

## What Must NOT Belong Here
- Binary checkpoint files or model weights.
- Checkpoints without recorded license terms.

## Source-of-Truth Relationship
- Referenced in experiment runs and governed by policies in `docs/13-governance/`.
