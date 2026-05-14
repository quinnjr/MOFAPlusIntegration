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

## Regenerating

```bash
python example/generate_test_data.py
```

Idempotent — overwrites the existing CSVs with the same seeded values.
