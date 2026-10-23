# RepoMedic — Known Limitations

## Current limitations

- Python-only analysis; no multi-language support.
- AST-based indexing does not resolve dynamic dispatch or reflection.
- Coverage signal not yet integrated.
- No LLM baseline comparison (requires model credentials).
- Frontend UI not yet built.
- Cost and latency not yet measured.
- Patch application not yet wired to UI approval flow.
- Experiment engine supports command-based experiments only.

## Security limitations

- Subprocess execution is not sandboxed; untrusted repositories should run in a container.
- Secret redaction is pattern-based and may miss unknown secret formats.
- Git worktree isolation is not a security boundary.
- No network isolation for executed commands.

## Measurement limitations

- Fixture set is small (4 projects, 5 known bugs).
- No statistical significance testing.
- Baseline comparison is qualitative only.
