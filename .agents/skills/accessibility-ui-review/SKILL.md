---
name: accessibility-ui-review
description: Accessibility (a11y) and responsive UX evaluation
---

# Accessibility and UI Review Skill

## 1. Purpose & When to Use
Use when developing or revising Vue components, navigation layouts, color tokens, and interactive widgets.

## 2. Inputs
- Vue component templates and styles.
- Design token contrast ratios.

## 3. Step-by-Step Runbook
1. **Semantic HTML**: Verify proper heading hierarchy (`h1`, `h2`), `nav`, `main`, and `button` elements.
2. **Keyboard Navigation**: Ensure all interactive controls are focusable and operable via `Tab` and `Enter`/`Space`.
3. **Contrast Ratio**: Confirm text against background meets WCAG 2.1 AA (at least 4.5:1 for normal text).
4. **ARIA Attributes**: Use `aria-label` on icon-only buttons and `role="status"` on live feedback badges.
5. **Responsive Check**: Test rendering at 800px, 1024px, and 1440px viewport widths.

## 4. Acceptance Criteria & Checklist
- [ ] Keyboard navigation fully functional.
- [ ] Visible focus outlines retained on all interactive elements.
- [ ] Zero accessibility contrast regressions.

## 5. Sources
- W3C WCAG 2.1 Guidelines
- Vue Accessibility Documentation: https://vuejs.org/guide/best-practices/accessibility.html
