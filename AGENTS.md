# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Skeleton repo — `MOFAPlusIntegration.py` and `test_mofa_plus_integration.py` do not exist yet. Only licensing, ignore rules, `requirements*.txt`, and synthetic example data are present. Implementation work means *creating* the plugin module and tests, following the contract documented in `../AGENTS.md` (workspace-level) and the sibling plugins listed in the README.

## What this plugin will be

A single-class PluMA plugin wrapping [`mofapy2`](https://github.com/bioFAM/mofapy2) for joint factor decomposition across aligned omics modalities. Inputs are per-modality CSVs (subjects × features); outputs are a factor matrix, per-modality feature weights, variance-explained breakdown, and a training summary. Use the sibling integration plugins as the template — `SNFIntegration`, `EarlyFusionIntegration`, `SHAPExplainability` — since each follows the same `input()/run()/output()` shape and parameter-file conventions.

## Example data

`example/` contains synthetic four-modality data (`transcriptomics.csv`, `metagenomics.csv`, `metabolomics.csv`, `proteomics.csv`) with embedded shared latent structure plus `true_factors.csv` ground truth and `groups.csv` for multi-group MOFA+. Regenerate with `python example/generate_test_data.py`. `parameters.txt` is the canonical parameter file (5 true latent factors, ask for `n_factors 8` so MOFA+ prunes inactive ones).

Note: `.gitignore` excludes `*.csv` — the example CSVs were committed with `git add -f` and any new committed synthetic data must use the same.

## Parameter file shape

Whitespace-delimited `key value` per line, `#` comments. Keys used by the example: per-modality view names → CSV path, optional `groups`, `n_factors`, `max_iter`, `convergence_mode`, `scale_views`, `seed`, `likelihood`. The plugin's `input(filename)` method must parse this format.

## Tests

`requirements-test.txt` pins `pytest` + `pytest-cov`. Once tests exist, run:

```bash
pip install -r requirements-test.txt
pytest -q                          # full suite
pytest test_mofa_plus_integration.py::test_name   # single test
```

No `pytest.ini` yet — add one when writing tests (sibling plugins have minimal configs to crib from).

## Branch model

Standard git-flow as defined in the work-profile global CLAUDE.md. Branch from `develop`, merge back via squash. There is no Jira project for the PluMA / Parkinson's thesis work, so the `<TICKET-ID>:` prefix in commits does not apply here — use plain Conventional Commits (`feat(mofa): ...`, `fix: ...`).
