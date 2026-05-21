# Example synthetic data

Self-contained synthetic dataset for MOFAPlusIntegration. All CSVs are produced by [`generate_test_data.py`](generate_test_data.py); they're committed so the plugin can be exercised without a numpy/pandas environment.

## Generative model

40 subjects, 5 true latent factors drawn from N(0, 1), four omics views built as `X_view = Z @ W_view + ε` with view-specific sparse loadings:

| View | n_features | Active factors | Feature prefix |
|---|---|---|---|
| transcriptomics | 60 | 1, 2, 3 | `Gene_*` |
| metagenomics | 40 | 2, 3, 4 | `Taxa_*` |
| metabolomics | 30 | 1, 4, 5 | `Metab_*` |
| proteomics | 50 | 1, 3, 5 | `Prot_*` |

Noise is i.i.d. N(0, 0.5²). Factor 1 has a +1.5 mean shift on the "case" group so the dataset is also useful for downstream classifier benchmarks. Seed is fixed at 42.

## Files

| File | Shape | Contents |
|---|---|---|
| `transcriptomics.csv` | 40 × 60 | Synthetic gene expression |
| `metagenomics.csv` | 40 × 40 | Synthetic taxa abundance |
| `metabolomics.csv` | 40 × 30 | Synthetic metabolite intensities |
| `proteomics.csv` | 40 × 50 | Synthetic protein abundances |
| `groups.csv` | 40 × 1 | `subject_id, group` (case / control split, factor-1 signal carrier) |
| `true_factors.csv` | 40 × 5 | Ground-truth latent factors — for evaluating factor recovery |
| `parameters.txt` | — | Example PluMA parameter file pointing at the CSVs above |
| `config.txt` | — | Minimal PluMA pipeline (`Prefix example/` + one `Plugin` line) |
| `run_pluma_example.sh` | — | One-shot wrapper: stages the plugin via `PLUMA_PLUGIN_PATH`, invokes pluma, runs the verifier |
| `verify_outputs.py` | — | Asserts all expected output files exist and that ≥ 3 of the 5 seeded factors are recovered with `|Pearson r|` ≥ 0.7 |

## Running through the pluma binary

```bash
./example/run_pluma_example.sh                    # uses `pluma` from $PATH
./example/run_pluma_example.sh /path/to/pluma     # explicit binary
PLUMA=/path/to/pluma ./example/run_pluma_example.sh
```

The script stages the plugin under a temporary `PLUMA_PLUGIN_PATH`
(`MOFAPlusIntegration/MOFAPlusIntegration.py` plus the
PluMA-convention `MOFAPlusIntegrationPlugin.py` adapter side-by-side),
invokes pluma against `example/config.txt` from the repo root, then
runs `verify_outputs.py` against the produced output prefix.

Outputs land at `example/out/mofa.{factors,weights_<view>,variance_explained,summary}.{csv,txt}`.

**Requirements**: `mofapy2`, `numpy`, `pandas`, `h5py` importable from
the Python interpreter pluma is linked against. If you're using PluMA's
shared-venv pattern (`resolve_requirements.py`), symlink this repo
under `<pluma>/plugins/MOFAPlusIntegration/` first and rerun `scons` so
those deps land in the venv automatically. Otherwise expose them via
`PYTHONPATH` (e.g. `PYTHONPATH=/path/to/venv/lib/python3.x/site-packages`).

Verified end-to-end on Python 3.14 + mofapy2 0.7.x: all 5 seeded latent
factors recovered with `|r| ≥ 0.99`.

## Regenerating the synthetic data

```bash
python example/generate_test_data.py
```

Idempotent — overwrites the existing CSVs with the same seeded values.
