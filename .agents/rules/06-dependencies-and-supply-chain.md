# Rule 06: Dependencies and Supply Chain Security

1. **Lockfile Integrity**: `pnpm-lock.yaml` is the single source of truth for dependencies. Always commit lockfile changes.
2. **Pin Dependencies**: Use exact or minor-pinned semver ranges. Never install unchecked dependencies.
3. **No Heavy ML Binaries**: Never install PyTorch, TorchVision, Transformers, or CUDA runtimes in this foundation.
4. **Audit Cleanliness**: Regular runs of `pnpm audit` must maintain zero high or critical security advisories.
