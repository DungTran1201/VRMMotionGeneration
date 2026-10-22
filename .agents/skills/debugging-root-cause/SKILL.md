---
name: debugging-root-cause
description: Systematic root cause analysis and defect isolation
---

# Debugging Root Cause Skill

## 1. Purpose & When to Use
Use when investigating failed builds, test regressions, runtime exceptions, or unexpected platform behavior.

## 2. Inputs
- Error message, stack trace, and terminal output.
- Failing test case or reproducible steps.

## 3. Step-by-Step Runbook
1. **Reproduce**: Execute the minimal command line reproducing the failure. Record exit code and output.
2. **Isolate**: Determine whether the defect is in contracts, build config, renderer, preload, or main process.
3. **Formulate Hypothesis**: State what condition causes the failure and classify as `INFERRED`.
4. **Write Failing Test**: Author a minimal test reproducing the defect.
5. **Apply Minimal Fix**: Implement the targeted fix without speculative side-effects.
6. **Verify Resolution**: Re-run the test and confirm exit code 0.

## 4. Acceptance Criteria & Checklist
- [ ] Root cause identified and documented.
- [ ] Regression test added to test suite.
- [ ] Full quality gate suite passes.

## 5. Sources
- Andreas Zeller, *Why Programs Fail: A Guide to Systematic Debugging*
- Antigravity Awesome Skills Debugging Patterns
