# Rule 02: Architecture Boundaries

1. **Dependency Direction**:
   - `frontend/apps/*` may import from `frontend/packages/*`.
   - `frontend/packages/*` MUST NEVER import from `frontend/apps/*`.
   - `frontend/packages/platform-contracts` has ZERO dependencies.
   - `frontend/packages/ui` must not import Electron or Node APIs.
2. **Desktop Isolation**:
   - Only `frontend/apps/desktop/src/main` and `preload` may reference Electron native APIs.
   - The renderer process interacts exclusively through `window.desktopAPI`.
3. **Backend Status**:
   - Server-side capabilities in `backend/` are `NOT IMPLEMENTED / OPTIONAL`.
   - Never force simple local features through mock HTTP loops.
