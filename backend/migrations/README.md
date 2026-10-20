# `backend/migrations/` — Database Schema Migrations

## Purpose
Maintains structured, version-controlled database schema migration scripts and revision histories.

## What Belongs Here
- Sequential migration scripts (SQL or framework-native migration tools such as Alembic).
- Schema version tracking and rollback definitions.
- Initial seed definitions for static system data (if applicable).

## What Must NOT Belong Here
- Production database dump files or sensitive user data.
- Ad-hoc, untracked SQLite files (`*.db`, `*.sqlite`).
- Business logic or kinematic transformation functions.

## Source-of-Truth Relationship
- Migration schemas must reflect data domain models declared in `models/domain/` and architecture specifications in `models/architecture/`.
