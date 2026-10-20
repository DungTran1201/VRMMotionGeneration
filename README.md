# VRMMotionGeneration

An engineering workspace for a web application dedicated to humanoid motion generation, kinematic retargeting, and real-time 3D avatar rendering (supporting VRM and rigged glTF/GLB models).

> **Important Notice: Structure & Governance Baseline**  
> This repository is currently in a scaffold and governance baseline state. Application source code, production technology stacks, and end-to-end capabilities are **not yet implemented or chosen**. Implementation will proceed following discovery, formal Architecture Decision Records (ADRs), and canonical modeling.

---

## Repository Layout

```text
VRMMotionGeneration/
├── .gitignore                      # Environment, checkpoint, cache, and archive exclusions
├── .agents/                        # Agent harness (rules, skills, agent profiles, configs)
├── AGENTS.md                       # Operation Dev operating contract
├── README.md                       # Project overview and baseline status
├── frontend/                       # Browser/client presentation application
│   ├── README.md
│   ├── apps/web/README.md          # Web application package placeholder
│   ├── public/README.md            # Static public web assets
│   └── tests/README.md             # Client unit & component tests
├── backend/                        # Server application, APIs, and kinematic services
│   ├── README.md
│   ├── src/README.md               # Backend application source placeholder
│   ├── migrations/README.md        # Database schema migrations
│   └── tests/README.md             # Backend unit & integration tests
├── infra/                          # Operations, deployment, CI, and tooling
│   ├── README.md
│   ├── scripts/README.md           # Developer & maintenance scripts
│   ├── ci/README.md                # Automated CI pipeline workflows
│   ├── deployment/README.md        # Deployment manifests & container specs
│   └── observability/README.md     # Monitoring, metrics, and health checks
├── docs/                           # Human-readable engineering lifecycle documentation
│   ├── README.md
│   ├── 00-discovery/README.md      # Discovery audits & exploratory findings
│   ├── 01-planning/README.md       # Roadmaps, milestones, and planning
│   ├── 02-requirements/README.md   # Functional & non-functional requirements
│   ├── 03-business-process/README.md # Business workflows & avatar lifecycles
│   ├── 04-use-cases/README.md      # Formal use case specifications
│   ├── 05-architecture/README.md   # System architecture & ADRs
│   ├── 06-domain/README.md         # Kinematics, skeleton rigs, & domain models
│   ├── 07-api/README.md            # REST & WebSocket API specifications
│   ├── 08-behavior/README.md       # State machines & streaming lifecycle
│   ├── 09-security/README.md       # Threat modeling & upload safety
│   ├── 10-ux/README.md             # UI design & 3D viewport experience
│   ├── 11-testing/README.md        # QA strategy & test matrices
│   ├── 12-operations/README.md     # Deployment runbooks & runtime ops
│   └── 13-governance/README.md     # Release criteria & license compliance
├── diagrams/                       # Derived visual projections (Mermaid/SVG)
│   ├── README.md
│   ├── context/README.md           # System context diagrams
│   ├── architecture/README.md      # High-level architecture diagrams
│   ├── processes/README.md         # Workflow & process flowcharts
│   ├── sequence/README.md          # Interaction & sequence diagrams
│   ├── state/README.md             # State machine diagrams
│   ├── data-flow/README.md         # Motion data flow diagrams
│   ├── deployment/README.md        # Physical deployment diagrams
│   └── ux/README.md                # UX navigation & wireframe flows
├── models/                         # Canonical machine-readable specifications (YAML/JSON)
│   ├── README.md
│   ├── context/README.md           # Boundary & external actor schemas
│   ├── requirements/README.md      # Machine-readable requirement models
│   ├── process/README.md           # Machine-readable process schemas
│   ├── architecture/README.md      # Component & interface specifications
│   ├── domain/README.md            # Kinematic & humanoid skeleton schemas
│   ├── api/README.md               # OpenAPI / AsyncAPI definitions
│   ├── interaction/README.md       # Protocol & interaction schemas
│   ├── security/README.md          # Security policy definitions
│   ├── ux/README.md                # UI component & design token specs
│   ├── testing/README.md           # Test vector & fixture schemas
│   └── deployment/README.md        # Infrastructure topology models
└── exp/                            # Standalone exploratory experiment workspace
    ├── README.md
    ├── AGENTS.md                   # Experiment-specific operating contract
    ├── .gitignore                  # Experiment weight & artifact ignore rules
    ├── experiments/README.md       # Experiment logbooks & notebooks
    ├── scripts/README.md           # Data processing & run scripts
    ├── environments/README.md      # Python/CUDA environment manifests
    ├── datasets/README.md          # Dataset references & licensing rules
    ├── checkpoints/README.md       # Model weight & checkpoint storage policy
    ├── artifacts/README.md         # Output logs, tensors, & metrics
    └── reports/README.md           # Experiment summary reports
```

---

## Architectural Principles

1. **Decoupled Architecture**: Strict separation between `frontend/` (client UI), `backend/` (services/APIs), and `infra/` (operations).
2. **Canonical Models as Source of Truth**: Machine-readable models in `models/` serve as the canonical source. `docs/` provide human-readable engineering context, while `diagrams/` provide derived visual views that cite source artifacts.
3. **Experiment Isolation**: The `exp/` directory is strictly isolated. No production code imports, shared runtime dependencies, or symlinks may connect `exp/` to the website product.
4. **Deterministic Fixtures**: Once implemented, the application must maintain a deterministic fixture path that functions offline without GPU or model weights.
5. **Verified Evidence**: All technical decisions, benchmark claims, and format capabilities must be supported by verifiable tests and logs.

For developer guidelines and agent operating contracts, see [AGENTS.md](file:///c:/Users/PC/Project/VRMMotionGeneration/AGENTS.md) and [.agents/README.md](file:///c:/Users/PC/Project/VRMMotionGeneration/.agents/README.md).