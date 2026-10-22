# Rule 05: Testing Standards and Quality Gates

1. **Gate Sequence**:
   - QG-01: `pnpm install --frozen-lockfile`
   - QG-02: `pnpm typecheck`
   - QG-03: `pnpm lint`
   - QG-04: `pnpm test`
   - QG-05: `pnpm build:web`
   - QG-06: `pnpm build:desktop`
   - QG-07: Electron security audit
   - QG-08: Zero legacy motion references
2. **Deterministic Offline Execution**:
   - All tests must run offline without external cloud dependencies or GPU hardware.
3. **Bugfix Policy**:
   - Every bugfix must include a reproduction test that fails before the fix and passes after.
