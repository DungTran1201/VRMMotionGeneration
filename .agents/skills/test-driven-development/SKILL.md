---
name: test-driven-development
description: Test-driven development workflow using Vitest
---

# Test-Driven Development Skill

## 1. Purpose & When to Use
Use when implementing new features, adapters, utilities, or state stores to ensure regression prevention and design modularity.

## 2. Inputs
- Feature requirements and acceptance criteria.
- Existing tests in `tests/` directories.

## 3. Step-by-Step Runbook
1. **Red Stage**: Write an automated test describing the desired behavior in Vitest (`describe`, `it`, `expect`). Run test and verify it fails for the expected reason.
2. **Green Stage**: Write the minimal code necessary to make the test pass.
3. **Refactor Stage**: Clean up code, remove duplication, and improve variable naming while keeping tests green.
4. **Edge Cases**: Add tests for null/undefined, error boundaries, empty collections, and offline states.

## 4. Acceptance Criteria & Checklist
- [ ] Test executes deterministically without network dependencies.
- [ ] 100% assertions pass.
- [ ] Zero lint or typecheck warnings introduced.

## 5. Sources
- Kent Beck, *Test Driven Development: By Example*
- Vitest Guide: https://vitest.dev/guide/
