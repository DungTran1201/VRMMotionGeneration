# Rule 03: TypeScript Quality and Typing Standards

1. **Strict Mode Mandatory**: `strict: true` must be enabled across all `tsconfig.json` configurations.
2. **No `any`**: The use of `any` is prohibited. Use `unknown` and type narrowing, Discriminated Unions, or generic type constraints.
3. **Explicit Return Types**: All exported public functions and API methods must declare explicit return types.
4. **Shared Types**: Cross-package interfaces must reside in `@vrm/platform-contracts` or `@vrm/shared`.
