# Workflow: Release Checklist

Mandatory verification checklist before tagging or publishing a release.

---

## Pre-Release Verification

- [ ] All tests pass: `pnpm test`
- [ ] TypeScript typecheck clean: `pnpm typecheck`
- [ ] Linter clean: `pnpm lint`
- [ ] Web production build clean: `pnpm build:web`
- [ ] Desktop production build clean: `pnpm build:desktop`
- [ ] Electron security audit clean (`contextIsolation`, `sandbox`, `nodeIntegration = false`)
- [ ] Zero legacy motion models, weights, or datasets in the tree
- [ ] Dependencies audit clean: `pnpm audit`
- [ ] Version bumped in `package.json` and `@vrm/shared`
- [ ] `CHANGELOG.md` updated with release notes
