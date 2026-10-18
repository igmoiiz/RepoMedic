# RepoMedic — Project Definition

## 1. Product summary

RepoMedic is a Python-first, local-first debugging intelligence platform. It investigates software failures, builds evidence-backed explanations, and presents a developer with a diagnostic report before proposing any code changes.

RepoMedic is **diagnostic-first**, not an autonomous coding agent. Its primary value is helping a developer understand:
- what failed;
- where the failure manifested;
- which source locations may have caused it;
- what evidence supports or contradicts each candidate cause;
- which experiment could distinguish competing hypotheses;
- what remains uncertain; and
- how a proposed repair should be verified.

## 2. Product principles

1. **Evidence before explanation.** Every material claim should link to a captured observation, source location, test result, or clearly labelled inference.
2. **Facts and hypotheses are different.** Never label a guess as verified.
3. **Uncertainty is a valid result.** Report insufficient evidence rather than inventing a cause.
4. **Real results only.** Never claim tests passed unless the test runner actually ran and returned a successful result.
5. **Human control.** No patch is applied to the user's working branch without explicit approval.
6. **Local-first.** Repository contents, reports, and state stay local by default. Any model-provider data transfer must be explicit and documented.
7. **Minimal scope.** Prefer the smallest complete and testable implementation over broad, unfinished functionality.
8. **Security by design.** Treat repository files, dependencies, tests, prompts, and tool output as potentially untrusted.
9. **Reproducibility.** Save enough structured event data to explain how a conclusion was reached.
10. **Maintainability.** Use clear names, typed interfaces where useful, small modules, and straightforward control flow. Avoid needless abstraction.

## 3. Intended users

- Developers debugging unfamiliar or inherited Python repositories.
- Engineers investigating regressions and failing tests.
- Students and small teams that need affordable debugging support.
- Developers reviewing diagnoses or patches proposed by coding agents.

## 4. MVP definition

The first release should support one complete workflow for Python repositories:

1. Select a local repository and validate the path.
2. Inspect Git state and protect pre-existing modifications.
3. Identify Python files, project metadata, and available test commands.
4. Run a user-selected pytest target only after explaining the command and receiving permission where required.
5. Capture exit status, stdout/stderr, duration, and traceback.
6. Parse relevant source locations and build a lightweight symbol/reference index.
7. Produce a small ranked list of root-cause hypotheses.
8. Attach evidence and counterevidence to hypotheses.
9. Recommend a targeted experiment.
10. Show a diagnostic report and investigation timeline.
11. Optionally propose a patch in an isolated Git worktree.
12. Run relevant verification and show a diff.
13. Apply a patch only after explicit user approval.

The MVP is complete only when the workflow is tested end-to-end on known, reproducible faulty Python projects.

## 5. Explicit non-goals for MVP

- Multi-language support.
- Cloud-hosted repository execution.
- Autonomous pushes, commits, or pull requests.
- Training a custom code model.
- Fully automatic repair of arbitrary bugs.
- IDE plugins.
- Mandatory multi-agent orchestration frameworks.
- Mandatory vector database or external database server.
- Silent collection or upload of repository content.
- Claiming complete security isolation from a container alone.

## 6. Initial supported cases

Prioritize reproducible Python failures:
- exceptions and tracebacks;
- failing pytest assertions;
- common input and boundary-condition bugs;
- incorrect data transformations;
- state mutation and control-flow defects;
- straightforward configuration/import issues where safe to diagnose.

The tool must distinguish a code defect from an environment/setup failure and must report when a failure cannot be reproduced.

## 7. Success criteria

The project must have:
- deterministic test fixtures with known faulty locations and expected behavior;
- a baseline comparison against traceback-only or basic LLM diagnosis;
- top-1 and top-5 fault-localization measurements;
- diagnosis correctness measured separately from repair success;
- regression rate, runtime, model calls, and cost measured where applicable;
- an end-to-end demo that does not rely on fabricated results.

Do not advertise accuracy percentages until measured and reproducible.

## 8. Product language

Use “diagnosis,” “candidate cause,” “evidence,” “experiment,” “verified,” and “unverified” precisely.
Avoid unsupported terms such as “guaranteed bug-free,” “fully autonomous,” or “always correct.”
