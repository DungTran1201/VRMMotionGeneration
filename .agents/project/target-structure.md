# Recommended Website Repository Layout

Follow the separation used by `AgentHarnessBuilderTools` (`ai-backend/`, `ai-frontend/`, `ai-infra/`, `docs/`, `assets/`, `packaging/windows/`) while preserving the current repository's import-safe `backend/` and `frontend/` names. Similarity should be architectural, not a directory rename for its own sake.

```text
VRMMotionGeneration/
├── AGENTS.md
├── .agents/
│   ├── README.md
│   ├── rules/
│   ├── skills/
│   ├── agents/
│   ├── hooks/
│   └── project/
├── backend/
│   ├── pyproject.toml
│   ├── src/motionbricks_vrm/
│   │   ├── api/                 # optional extraction from app.py as it grows
│   │   ├── schemas/             # canonical contracts
│   │   ├── source_adapter/      # MotionBricks and future motion sources
│   │   ├── reconstruction/      # source feature decoding / kinematics
│   │   ├── retargeting/         # canonical motion -> target skeleton
│   │   ├── services/            # orchestration, jobs, status
│   │   └── streaming/           # websocket sessions
│   └── tests/
├── frontend/
│   ├── package.json
│   ├── public/
│   ├── src/
│   │   ├── app/                 # bootstrap and composition
│   │   ├── avatar/              # format loaders and scene/avatar lifecycle
│   │   ├── skeleton/            # rig inspection and profiles
│   │   ├── retargeting/         # browser-side target adapters if needed
│   │   ├── animation/           # buffer, clock, interpolation, playback
│   │   ├── transport/           # REST/WebSocket client
│   │   └── ui/
│   └── tests/
├── configs/
│   ├── canonical_motion.yaml
│   └── retarget_profiles/
├── fixtures/                    # small synthetic/test assets only; no unlicensed avatars
├── assets/                      # own/licensed docs and UI assets; avoid model weights
├── infra/                       # CI, local services, deployment templates
├── packaging/windows/            # only if installer/distribution is added
├── scripts/                      # developer tooling and validation entry points
├── docs/
│   ├── 01-planning/
│   ├── 02-requirements/
│   ├── 03-architecture/
│   ├── 04-api-and-data-contracts/
│   ├── 05-testing-and-quality/
│   ├── 06-deployment-and-operations/
│   ├── 07-security-and-licensing/
│   └── diagrams/
└── .github/workflows/
```

## Migration policy
- Do not move the current code into this layout wholesale in one operation.
- First capture a tree, import graph, routes, tests, and CI scripts.
- Create only missing boundaries that have a consumer; avoid empty directories added for appearance.
- If extracting modules from `app.py` or renaming a package, do one bounded change at a time, preserve public imports/API contracts, and run backend + frontend tests after each migration.
- Do not rename `backend/` to `ai-backend/` or `frontend/` to `ai-frontend/` without a separate approved migration, since current docs, commands, and import paths use existing names.
