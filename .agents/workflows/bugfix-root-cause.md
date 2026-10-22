# Workflow: Bugfix and Root Cause Analysis

Runbook for investigating, isolating, and fixing defects without introducing regressions.

---

## Phases

1. **Reproduction**: Capture reproducible command or interaction steps.
2. **Defect Isolation**: Isolate failure to contracts, build config, renderer, preload, or main process.
3. **Regression Test**: Author a Vitest test that fails on current code.
4. **Remediation**: Implement minimal fix behind stable interfaces.
5. **Verification**: Confirm regression test passes and no secondary quality gates fail.
