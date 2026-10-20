# Hook scripts and host integration

There is no universal hook API shared by all coding-agent products. These scripts are portable operations; configure Antigravity/Codex/other hosts to invoke them using that host's supported lifecycle events.

- `validate_agent_assets.py`: validates this harness' metadata and required files.
- `pre_commit.ps1`: checks staged whitespace, obvious secrets and large/checkpoint assets.
- `install-git-hooks.ps1`: installs `.git/hooks/pre-commit` that invokes `pre_commit.ps1` through PowerShell.
- `run_quality_gates.ps1`: runs backend tests, frontend tests/build when dependencies are installed, and agent-asset validation.

Do not claim “automatic after every edit” unless the chosen host actually registers the script as a post-edit hook. Git pre-commit runs only at commit time.
