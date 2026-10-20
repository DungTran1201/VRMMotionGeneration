# ARDY Model Checkpoints Directory

Stores local pretrained weights for ARDY models. Checkpoint binary files are gitignored.

## Target Model
- **Identifier:** `ARDY-Core-RP-20FPS-Horizon8`
- **Skeleton:** `CoreSkeleton27` (27 humanoid joints)
- **Native FPS:** 20.0
- **Prediction Horizon:** 8 frames (0.4s autoregressive step)
- **Source:** https://huggingface.co/nvidia/ARDY-Core-RP-20FPS-Horizon8
- **Files:** `denoiser.safetensors` (~623 MB), `tokenizer.safetensors` (~142 MB), `config.yaml`
- **License:** NVIDIA Open Model License
