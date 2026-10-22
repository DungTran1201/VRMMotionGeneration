# Rule 01: Evidence Not Assumptions

1. **Classification Standard**: Every technical claim must be explicitly classified as:
   - `VERIFIED`: Confirmed via command execution, log evidence, or passing tests.
   - `OBSERVED`: Inspected directly in the filesystem or Git tree.
   - `INFERRED`: Derived logically from verified facts with rationale explained.
   - `UNVERIFIED`: An assumption that requires live testing.
   - `BLOCKED`: Prevented by an environmental constraint, missing access, or missing dependency.
   - `NOT APPLICABLE`: Out of scope.
2. **No Mocked Test Claims**: Never report that tests or builds passed unless the command executed and returned exit code 0.
3. **No Unsubstantiated Push Claims**: Never declare "pushed to GitHub" unless `git push` succeeded and remote verification confirmed the commit SHA.
