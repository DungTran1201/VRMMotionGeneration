# `infra/observability/` — Monitoring, Metrics & Observability

## Purpose
Maintains observability configurations, logging formats, performance tracing templates, and health check definitions.

## What Belongs Here
- Structured logging configuration schemas.
- Health check and readiness probe endpoint configurations.
- Metric collection rules (e.g. Prometheus / OpenTelemetry configurations).

## What Must NOT Belong Here
- Production log files, execution traces, or user telemetry dumps.
- Application business logic.

## Source-of-Truth Relationship
- Observability requirements are derived from `docs/12-operations/` and non-functional requirements in `docs/02-requirements/`.
