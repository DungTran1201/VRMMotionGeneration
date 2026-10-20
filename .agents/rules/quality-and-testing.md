# Quality Gates and Test Strategy

## Backend
- Unit test schema validators, coordinate transforms, 6D rotation conversion, quaternion conversion, G1 hierarchy reconstruction, retarget composition, and error paths.
- API test health, schema/validation errors, unavailable checkpoints, real-inference initialization failure, upload limits and WebSocket disconnect/backpressure behavior.
- Add a smoke test that proves real inference produces a non-empty valid motion only when actual weights and upstream implementation are present. Stub/mocked tests must say they are mocked.

## Frontend
- Test schema validation, loader error states, skeleton inspection, bone profile mapping, coordinate conversion, root motion, slerp interpolation, playback controls, stop/dispose behavior, and unsupported format rejection.
- Include at least one licensed or synthetic rigged GLB fixture and a VRM test fixture where licensing permits. Do not check in private/proprietary avatars.
- Ensure switching avatars disposes geometry/materials/textures and cancels old animation/session state.

## Integration and performance
- Verify fixture mode offline without checkpoints.
- Verify API/WS payloads against the same canonical schema.
- Measure inference latency separately from decode, retarget, network, and rendering. Do not compare unlike measurements as if they were equivalent.
- Keep numeric tolerances explicit for quaternions, transformations and timestamps.
- Run backend tests, frontend tests, production build, static validation, and `git diff --check` for relevant changes.
- If tests cannot run, report the blocker and do not call the task verified.
