---
name: vue-typescript-implementation
description: Implement robust, type-safe Vue 3 components and design systems
---

# Vue 3 and TypeScript Implementation Skill

## 1. Purpose & When to Use
Use when implementing or modifying UI views, reusable components, layouts, or reactive state stores in `@vrm/ui` or apps.

## 2. Inputs
- Component requirements or UX wireframe.
- Design tokens (`tokens.css`) and platform contracts (`@vrm/platform-contracts`).

## 3. Step-by-Step Runbook
1. **Define Types**: Specify component props, emits, and internal state interfaces.
2. **Setup Script**: Use `<script setup lang="ts">` with typed props via `defineProps<{ ... }>()`.
3. **Use Design Tokens**: Apply CSS variables defined in `@vrm/ui/src/styles/tokens.css` for background, text, borders, and transitions.
4. **Handle Edge States**: Implement clear loading, error, empty, and not-available representations.
5. **Enforce Boundary**: Never import Node.js, Electron, or filesystem modules into Vue components.
6. **Verify Build**: Run `pnpm typecheck` and `pnpm build:web`.

## 4. Acceptance Criteria & Checklist
- [ ] TypeScript strict mode satisfied (zero errors).
- [ ] No hardcoded colors or ad-hoc inline styles.
- [ ] Accessible semantic HTML used with unique element IDs.

## 5. Sources
- Official Vue 3 Documentation: https://vuejs.org/guide/
- TypeScript Handbook: https://www.typescriptlang.org/docs/
