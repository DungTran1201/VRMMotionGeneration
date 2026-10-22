---
name: browser-e2e-playwright
description: Automated browser and end-to-end testing with Playwright
---

# Browser E2E Playwright Skill

## 1. Purpose & When to Use
Use for validating end-to-end user navigation, responsive viewport rendering, and browser smoke tests.

## 2. Inputs
- Running local dev server or preview build (`http://localhost:5173`).
- Playwright configuration file (`playwright.config.ts`).

## 3. Step-by-Step Runbook
1. **Target View**: Specify the target route (`/`, `/settings`, `/diagnostics`).
2. **Execute Assertions**: Check page title, header presence, view switching, and state transitions.
3. **Inspect Console**: Verify zero unhandled browser console errors or failed network requests.
4. **Clean Exit**: Terminate browser instances upon test completion.

## 4. Acceptance Criteria & Checklist
- [ ] Viewport renders responsively across desktop and tablet widths.
- [ ] Zero unhandled JavaScript exceptions in the browser.
- [ ] Accessible DOM selectors used (`getByRole`, `getByTestId`).

## 5. Sources
- Official Playwright Docs: https://playwright.dev/docs/intro
