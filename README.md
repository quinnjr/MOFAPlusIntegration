# MOFAPlusIntegration

A PluMA plugin wrapping [MOFA+](https://github.com/bioFAM/mofapy2) (Multi-Omics Factor Analysis v2) for joint dimensionality reduction across heterogeneous omics modalities.

## Background

MOFA+ decomposes two or more aligned omics matrices (samples × features per modality) into a shared latent factor space plus per-modality feature loadings. Each factor captures co-variation across modalities, so downstream classifiers can regress factor scores against phenotype without paying the cost of high-dimensional, modality-specific feature spaces.

This plugin follows the same convention as sibling integration plugins:

- [SNFIntegration](https://github.com/quinnjr/SNFIntegration) — Similarity Network Fusion
- [SHAPExplainability](https://github.com/quinnjr/SHAPExplainability) — SHAP feature attribution
- [EarlyFusionIntegration](https://github.com/quinnjr/EarlyFusionIntegration) — concatenation + LASSO/ElasticNet selection

## Plugin interface

The plugin follows the standard PluMA contract used by sibling
integration plugins:

```text
MOFAPlusIntegration.py
test_mofa_plus_integration.py
requirements.txt
example/
```

Inputs:
- per-modality CSVs (subjects × features)

Outputs:
- latent factor matrix
- per-modality feature weights
- variance explained metrics
- training summary

## Example Usage

```python
from MOFAPlusIntegration import MOFAPlusIntegration

plugin = MOFAPlusIntegration()

plugin.input("example/parameters.txt")

plugin.run()

plugin.output("example/output")
```

## Outputs

The plugin generates:

- `output.factors.csv`
- `output.weights_transcriptomics.csv`
- `output.weights_metagenomics.csv`
- `output.weights_metabolomics.csv`
- `output.weights_proteomics.csv`
- `output.variance_explained.csv`
- `output.summary.txt`

## Testing

Run the test suite with:

```bash
pytest -v
```

Skip slow MOFA+ training tests:

```bash
pytest -m "not slow"
```

## Synthetic Dataset

Synthetic test data with embedded shared latent structure is included
in [`example/`](example/).

Regenerate the dataset with:

```bash
python example/generate_test_data.py
```

Ground-truth latent factors used for validation are stored in:

```text
example/true_factors.csv
```

## References

- Argelaguet R, Velten B, Hernandez-Cabrera D, et al. (2018). Multi-Omics Factor Analysis — a framework for unsupervised integration of multi-omics data sets. *Mol Syst Biol* 14:e8124. [doi:10.15252/msb.20178124](https://doi.org/10.15252/msb.20178124)
- Argelaguet R, Arnol D, Bredikhin D, et al. (2020). MOFA+: a statistical framework for comprehensive integration of multi-modal single-cell data. *Genome Biol* 21:111. [doi:10.1186/s13059-020-02015-1](https://doi.org/10.1186/s13059-020-02015-1)

## License

MIT — see [LICENSE](LICENSE).
