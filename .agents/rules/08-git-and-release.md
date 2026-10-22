# Rule 08: Git Hygiene and Release Rules

1. **Trunk Safety**: Never direct-push to `main`. Work on feature or chore branches.
2. **Zero Force-Push**: Never use `git push --force` or `git push --force-with-lease` on shared or reset branches.
3. **No Unverified Claims**: A release or push is only considered complete when remote confirmation (`git ls-remote`) confirms the branch and commit SHA.
4. **Clean Commits**: Never commit `.env`, secrets, credentials, backups, or large binary checkpoints.
