# RepoMedic — Benchmark

## Reproducing benchmarks

Run all tests including benchmarks:

```powershell
python -m pytest tests/integration/test_benchmark.py -v --tb=short
```

Run security tests:

```powershell
python -m pytest tests/security/ -v --tb=short
```

Run full test suite:

```powershell
python -m pytest tests/ -v --tb=short
```

## Fixture projects

Located in `tests/fixtures/buggy_projects/`:

| Fixture | Bug type | Buggy file | Buggy line |
|---|---|---|---|
| divide_by_zero | ZeroDivisionError | src/calc.py | 2 |
| off_by_one | IndexError | src/sequence.py | 2 |
| wrong_comparison | Wrong operator | src/compare.py | 7 |
| wrong_comparison | Wrong operator | src/compare.py | 11 |
| infinite_loop | Infinite loop | src/loop.py | 4 |

## Metrics

- Top-1 localization: does the top-ranked location match the known buggy line?
- Top-5 localization: is the buggy line in the top 5 ranked locations?
- Determinism: identical evidence produces identical ranking?

## Baseline comparison

Traceback-only baseline: use the raw traceback frame as the predicted location.
RepoMedic: use evidence-weighted ranking with call-path expansion.

## Known limitations

- Fixtures are small and deterministic; real-world accuracy may vary.
- No LLM baseline measured yet (requires model credentials).
- Cost and latency not yet measured.
