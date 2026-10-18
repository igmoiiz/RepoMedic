# RepoMedic — Security Policy and Threat Model

## 1. Security objectives

RepoMedic inspects and may execute code from local repositories. A repository can contain malicious code, misleading instructions, hostile test fixtures, dependency install hooks, and secrets. Treat repository content as untrusted input, even when it appears to be documentation.

Security priorities:
1. Protect the host machine and user files.
2. Prevent unauthorized network access and secret exfiltration.
3. Preserve the user's original working tree and Git state.
4. Prevent unapproved code changes.
5. Keep local data private by default.
6. Make execution and data-transfer boundaries visible.

## 2. Threat actors and assets

### Threats
- A malicious or compromised repository.
- A dependency with installation-time or runtime code execution.
- Prompt injection in source files, README files, comments, test output, or issue descriptions.
- An LLM suggesting destructive commands or unsafe patches.
- Path traversal or symlink attacks.
- Resource exhaustion from infinite tests, huge output, recursion, or large files.
- Accidental disclosure through logs, prompts, reports, telemetry, or model-provider requests.
- Accidental loss of user changes during patch application.

### Assets
- Source code and intellectual property.
- API keys, SSH keys, `.env` files, cloud credentials, and local configuration.
- Files outside the selected repository.
- Git working-tree changes and uncommitted work.
- Local reports and investigation history.
- Model-provider credentials and usage limits.

## 3. Trust boundaries

Separate these domains:
1. RepoMedic application code.
2. Repository content being analyzed.
3. Code execution environment.
4. LLM provider and any remote service.
5. User's original working tree.
6. Patch worktree.
7. Local persistent data.

Content crossing a boundary must be validated and minimized. Repository text is data, not trusted instructions. Model output is untrusted input, not authorization.

## 4. Safe defaults

- Default to local-only metadata and persistence.
- Clearly disclose that sending code to a hosted model sends selected content to that provider.
- Never upload a full repository by default.
- Exclude secret files, credentials, private keys, `.env*` files, virtual environments, caches, build outputs, and large binaries from indexing and model context.
- Add an explicit, reviewable allowlist for any content sent to a model.
- Redact known secret patterns from logs and reports; do not claim redaction is perfect.
- Never store provider API keys in the repository or SQLite event log.
- Use environment variables or a user-local secret store for credentials.
- Do not log raw environment variables.
- Avoid telemetry in the MVP.
- Set execution timeouts, output caps, file-size caps, and investigation budgets.
- Validate all user-supplied paths and resolve them before access.
- Detect and handle symlinks carefully; do not follow paths outside approved roots.
- Use parameterized SQL.
- Bind the local API to loopback by default; do not expose it to the LAN unless explicitly configured.
- Apply CSRF/origin protections if the browser UI can invoke state-changing local API actions.
- Keep dependency versions reproducible and update dependencies deliberately.

## 5. Command execution policy

Never build a shell command by concatenating user text or LLM output.

- Prefer subprocess argument arrays with `shell=False`.
- Allow only known executable paths and supported argument patterns by default.
- Display the command, target directory, and expected effects before running commands that may execute repository code.
- Require explicit user authorization for execution of untrusted project code.
- Use timeouts, cancellation, bounded stdout/stderr, and process cleanup.
- Do not allow model-generated commands to execute automatically.
- Do not allow execution to read arbitrary host files or access the network by default.
- Dependency installation can execute code. Treat it as a separate, high-risk operation requiring explicit approval.
- Never run `sudo`, destructive disk commands, credential-management commands, or host-level changes on behalf of a repository agent.

## 6. Isolation model

Trusted local repositories may be supported first with clear warnings. Untrusted repositories require a restricted execution environment.

Preferred defense-in-depth controls:
- dedicated unprivileged user or isolated VM/container;
- read-only source mount for diagnostic runs when practical;
- separate writable scratch/worktree;
- no host credentials mounted into the execution environment;
- network disabled unless explicitly approved;
- CPU, memory, process, file-size, and wall-clock limits;
- restricted filesystem visibility;
- clean environment variables;
- disposable environment for untrusted runs.

A standard container is not a complete security boundary. For high-risk untrusted code, use a hardened sandbox or VM and test the threat model before claiming safety.

## 7. Patch safety

- Never edit the original working tree during diagnosis.
- Record the initial Git status and preserve pre-existing changes.
- Generate patches in an isolated worktree.
- Reject path traversal, absolute-path targets, unexpected binary changes, symlink escapes, and changes outside allowed paths.
- Show the full diff before application.
- Run verification in the isolated worktree.
- Require a distinct explicit approval before applying the patch to the user's working branch.
- Do not commit or push automatically.
- If the repository state changed since the patch was prepared, invalidate or rebase the proposal safely and ask for review again.
- Never overwrite uncommitted user work.

## 8. Prompt-injection resistance

- Treat repository instructions, comments, README content, test output, and issue text as untrusted data.
- Do not follow instructions found in repository content that ask to reveal secrets, change system policies, or execute unrelated commands.
- Give the model only the tools and data required for the current diagnostic step.
- Use structured outputs validated against schemas.
- Keep authorization decisions in deterministic application code, not in the model.
- Tool outputs must be labeled as observations, not trusted instructions.
- Validate every proposed file path, command, and patch independently.

## 9. Data retention and privacy

- Keep investigation data local by default.
- Provide a way to delete local sessions and generated artifacts.
- Avoid persisting full source files when source references and limited excerpts suffice.
- Set size and retention limits for stdout/stderr and reports.
- Clearly identify which evidence was sent to a remote provider.
- Never include secrets in diagnostic exports.
- Do not add telemetry without explicit user consent and documentation.

## 10. Security testing checklist

- [ ] Path traversal attempts are rejected.
- [ ] Symlink escape attempts are rejected.
- [ ] `.env`, keys, tokens, and credentials are excluded from indexing and prompts.
- [ ] Huge files and binary files are skipped safely.
- [ ] Infinite tests time out and child processes are cleaned up.
- [ ] Output caps work for stdout and stderr.
- [ ] Cancellation does not leave orphaned processes.
- [ ] Model-generated commands cannot bypass policy.
- [ ] Malformed model output is rejected safely.
- [ ] A malicious README cannot authorize tool execution.
- [ ] A patch cannot write outside the isolated worktree.
- [ ] Existing user changes remain untouched.
- [ ] Patch application is impossible without explicit approval.
- [ ] Local API binds to loopback by default.
- [ ] Provider errors do not leak secrets or raw environment variables.
- [ ] Tests run without requiring live API credentials.

## 11. Incident response

If a security issue is discovered:
1. Stop affected execution or patch application.
2. Preserve minimal, non-sensitive diagnostic information.
3. Identify affected versions and trust boundaries.
4. Reproduce the issue in a disposable environment.
5. Add a regression test.
6. Fix the underlying cause and review adjacent paths.
7. Document residual risk before release.

## 12. Security claims

Do not claim that RepoMedic is “secure,” “sandboxed,” or “safe for arbitrary repositories” merely because it uses containers, a virtual environment, or an LLM provider's safety features. Claims must be limited to controls that are implemented and tested.
