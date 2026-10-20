---
name: release-readiness
description: Prepare a verifiable release without overstating support.
---

\
# Release Readiness

1. Verify the requested behavior against acceptance criteria.
2. Run backend tests, frontend tests/build, agent asset validator, staged diff check and applicable security tests.
3. Check README/setup docs, .env.example, configuration defaults, CORS, upload policy, API schema and license notices.
4. Ensure no checkpoint binaries, secrets, user avatar assets or generated build directories are staged.
5. Review all unsupported/incomplete pathways, including real inference stubs and optional format adapters.
6. Confirm the UI reports actual runtime mode, loaded avatar type, rig readiness and inference errors.
7. Write release notes listing verified formats, tested environments, commands/results, limitations, rollback instructions and model/source license distinction.
