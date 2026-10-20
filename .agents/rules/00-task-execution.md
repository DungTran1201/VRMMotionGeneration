# Task Execution and Evidence Rules

- Inspect before editing: `git status --short`, key config files, affected source, related tests, and linked docs.
- For more than a local one-file fix, state scope, plan, risks, and acceptance criteria first.
- Prefer small, reversible changes. Avoid broad renames/reformatting unrelated to the task.
- Never fabricate test output, benchmark numbers, inference success, or file existence. Distinguish “not run”, “blocked”, “passed”, and “failed”.
- Do not delete or overwrite user data or uncommitted changes. If a destructive migration is required, create a reversible migration and document backup/rollback.
- Use progressive disclosure: root `AGENTS.md` remains short; open only task-relevant skills/rules/docs.
- Final response reports behavior changed, files changed, commands run and results, known limitations, and next logical work.
